"""Chat API endpoints for AI Todo Chatbot."""
import json
from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from typing import Optional

from app.api.deps import SessionDep, CurrentUser
from app.schemas.chat import (
    SendMessageRequest,
    MessageResponse,
    ChatResponse,
    ConversationResponse,
    ConversationWithMessagesResponse,
    ConversationListResponse,
    TitleGenerationResponse,
    UnifiedChatRequest,
    UnifiedChatResponse,
    ToolCallInfo,
    ChatStreamRequest,
)
from app.services.conversation_service import ConversationService
from app.services.ai.agents.orchestrator import process_message, process_message_streamed, get_agent_icon
from app.middleware.rate_limit import check_rate_limit

router = APIRouter()


@router.post("", response_model=UnifiedChatResponse)
async def unified_chat(
    request: UnifiedChatRequest,
    session: SessionDep,
    current_user: CurrentUser,
):
    """Send a message and get AI response.

    Creates a new conversation if conversation_id is not provided.
    Rate limited to 5 messages per minute per user.
    Message content limited to 1000 characters.

    This is the primary chat interface that handles both new and existing
    conversations in a single endpoint.
    """
    # Check rate limit
    await check_rate_limit(current_user)

    service = ConversationService(session)

    # Auto-create conversation if not provided
    if request.conversation_id:
        conversation = service.get_conversation(request.conversation_id, current_user)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
    else:
        try:
            conversation = service.create_conversation(current_user)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    # Save user message
    user_message = service.add_message(
        conversation_id=conversation.id,
        user_id=current_user,
        role="user",
        content=request.message,
    )

    if not user_message:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save message"
        )

    # Get conversation history for context
    messages = service.get_messages(conversation.id, current_user)
    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in messages[:-1]  # Exclude the message we just added
    ]

    # Process message through AI orchestrator
    result = await process_message(
        user_id=current_user,
        message=request.message,
        conversation_history=conversation_history,
    )

    # Save assistant response
    assistant_message = service.add_message(
        conversation_id=conversation.id,
        user_id=current_user,
        role="assistant",
        content=result.get("content", "I'm sorry, I couldn't process that request."),
        agent_name=result.get("agent_name", "Aren"),
        agent_icon=result.get("agent_icon", "🤖"),
    )

    if not assistant_message:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save AI response"
        )

    # Extract tool calls from result (now a simple list of strings)
    tool_calls = []
    if "tool_calls" in result and result["tool_calls"]:
        tool_calls = [
            ToolCallInfo(tool_name=tc, success=True)
            for tc in result["tool_calls"]
        ]

    return UnifiedChatResponse(
        conversation_id=conversation.id,
        response=assistant_message.content,
        tool_calls=tool_calls,
        agent_name=result.get("agent_name", "Aren"),
        agent_icon=result.get("agent_icon", "🤖"),
    )


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    session: SessionDep,
    current_user: CurrentUser,
):
    """Create a new conversation.

    Returns 400 if user has reached maximum conversations (100).
    """
    service = ConversationService(session)

    try:
        conversation = service.create_conversation(current_user)
        return conversation
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    session: SessionDep,
    current_user: CurrentUser,
    limit: int = Query(default=50, le=100, ge=1),
    offset: int = Query(default=0, ge=0),
):
    """List user conversations with pagination."""
    service = ConversationService(session)

    conversations = service.get_user_conversations(
        user_id=current_user,
        limit=limit,
        offset=offset,
    )
    total = service.count_user_conversations(current_user)

    return ConversationListResponse(
        conversations=conversations,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationWithMessagesResponse)
async def get_conversation(
    conversation_id: str,
    session: SessionDep,
    current_user: CurrentUser,
):
    """Get a conversation with all its messages."""
    service = ConversationService(session)

    conversation = service.get_conversation_with_messages(
        conversation_id=conversation_id,
        user_id=current_user,
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    return conversation


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    session: SessionDep,
    current_user: CurrentUser,
):
    """Delete a conversation and all its messages."""
    service = ConversationService(session)

    deleted = service.delete_conversation(
        conversation_id=conversation_id,
        user_id=current_user,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    return {"success": True, "message": "Conversation deleted"}


@router.post("/conversations/{conversation_id}/messages", response_model=ChatResponse)
async def send_message(
    conversation_id: str,
    request: SendMessageRequest,
    session: SessionDep,
    current_user: CurrentUser,
):
    """Send a message and get AI response.

    Rate limited to 5 messages per minute per user.
    Message content limited to 1000 characters.
    """
    # Check rate limit
    await check_rate_limit(current_user)

    service = ConversationService(session)

    # Verify conversation exists and belongs to user
    conversation = service.get_conversation(conversation_id, current_user)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Save user message
    user_message = service.add_message(
        conversation_id=conversation_id,
        user_id=current_user,
        role="user",
        content=request.content,
    )

    if not user_message:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save message"
        )

    # Get conversation history for context
    messages = service.get_messages(conversation_id, current_user)
    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in messages[:-1]  # Exclude the message we just added
    ]

    # Process message through AI orchestrator
    result = await process_message(
        user_id=current_user,
        message=request.content,
        conversation_history=conversation_history,
    )

    # Save assistant response
    assistant_message = service.add_message(
        conversation_id=conversation_id,
        user_id=current_user,
        role="assistant",
        content=result.get("content", "I'm sorry, I couldn't process that request."),
        agent_name=result.get("agent_name", "Aren"),
        agent_icon=result.get("agent_icon", "🤖"),
    )

    if not assistant_message:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save AI response"
        )

    return ChatResponse(
        message=MessageResponse(
            id=assistant_message.id,
            role=assistant_message.role,
            content=assistant_message.content,
            agent_name=assistant_message.agent_name,
            agent_icon=assistant_message.agent_icon,
            created_at=assistant_message.created_at,
        ),
        agent_name=result.get("agent_name", "Aren"),
        agent_icon=result.get("agent_icon", "🤖"),
        tool_calls=result.get("tool_calls", []),
    )


@router.post("/conversations/{conversation_id}/title", response_model=TitleGenerationResponse)
async def generate_title(
    conversation_id: str,
    session: SessionDep,
    current_user: CurrentUser,
):
    """Generate an AI title for the conversation based on its content."""
    service = ConversationService(session)

    # Get conversation with messages
    conversation = service.get_conversation_with_messages(conversation_id, current_user)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    if not conversation.messages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conversation has no messages to generate title from"
        )

    # Generate title from first few messages
    # For now, use a simple approach - take first user message as title basis
    first_user_message = next(
        (msg for msg in conversation.messages if msg.role == "user"),
        None
    )

    if first_user_message:
        # Truncate to create a title
        title = first_user_message.content[:50]
        if len(first_user_message.content) > 50:
            title += "..."
    else:
        title = "New Conversation"

    # Update conversation title
    updated = service.update_conversation_title(
        conversation_id=conversation_id,
        user_id=current_user,
        title=title,
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update title"
        )

    return TitleGenerationResponse(title=title)


@router.post("/stream")
async def stream_chat(
    request: ChatStreamRequest,
    session: SessionDep,
    current_user: CurrentUser,
):
    """Stream AI response using Server-Sent Events (SSE).

    Creates a new conversation if conversation_id is not provided.
    Returns streaming response with real-time token delivery.

    SSE Event Types:
    - conversation_created: New conversation ID (if created)
    - agent_change: Agent handoff notification with name and icon
    - token: Text chunk from AI response
    - tool_call: MCP tool invocation notification
    - done: Stream completion with message_id
    - error: Error notification

    Rate limited to 5 messages per minute per user.
    """
    # Check rate limit
    await check_rate_limit(current_user)

    service = ConversationService(session)
    conversation_created = False

    # Auto-create conversation if not provided
    if request.conversation_id:
        conversation = service.get_conversation(request.conversation_id, current_user)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
    else:
        try:
            conversation = service.create_conversation(current_user)
            conversation_created = True
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    # Save user message
    user_message = service.add_message(
        conversation_id=conversation.id,
        user_id=current_user,
        role="user",
        content=request.message,
    )

    if not user_message:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save message"
        )

    # Get optimized conversation context
    conversation_history = service.get_optimized_context(
        conversation_id=conversation.id,
        user_id=current_user,
        context_window=request.context_window,
    )
    # Remove the message we just added from context
    if conversation_history and conversation_history[-1].get("content") == request.message:
        conversation_history = conversation_history[:-1]

    async def generate_sse():
        """Generate SSE events from streaming response."""
        accumulated_content = ""
        final_agent_name = "Aren"
        final_agent_icon = "🤖"

        # Emit conversation_created event if new conversation
        if conversation_created:
            yield f"data: {json.dumps({'type': 'conversation_created', 'conversation_id': conversation.id})}\n\n"

        try:
            async for event in process_message_streamed(
                user_id=current_user,
                message=request.message,
                conversation_history=conversation_history,
                language_hint=request.language_hint.value,
            ):
                event_type = event.get("type")

                if event_type == "token":
                    accumulated_content += event.get("content", "")
                    yield f"data: {json.dumps(event)}\n\n"

                elif event_type == "agent_change":
                    final_agent_name = event.get("agent", "Aren")
                    final_agent_icon = event.get("icon", "🤖")
                    yield f"data: {json.dumps(event)}\n\n"

                elif event_type == "tool_call":
                    yield f"data: {json.dumps(event)}\n\n"

                elif event_type == "done":
                    # Use accumulated content or final content from event
                    final_content = accumulated_content or event.get("content", "")

                    # Save assistant message to database
                    assistant_message = service.add_message(
                        conversation_id=conversation.id,
                        user_id=current_user,
                        role="assistant",
                        content=final_content,
                        agent_name=final_agent_name,
                        agent_icon=final_agent_icon,
                    )

                    message_id = assistant_message.id if assistant_message else ""
                    yield f"data: {json.dumps({'type': 'done', 'message_id': message_id})}\n\n"

                elif event_type == "error":
                    yield f"data: {json.dumps(event)}\n\n"

        except Exception as e:
            import logging
            logging.error(f"SSE streaming error: {type(e).__name__}: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': 'Streaming error occurred'})}\n\n"

    return StreamingResponse(
        generate_sse(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
