"""Chat API endpoints for AI Todo Chatbot."""
from fastapi import APIRouter, HTTPException, status, Query
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
)
from app.services.conversation_service import ConversationService
from app.services.ai.agents.orchestrator import process_message, get_agent_icon
from app.middleware.rate_limit import check_rate_limit

router = APIRouter()


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
