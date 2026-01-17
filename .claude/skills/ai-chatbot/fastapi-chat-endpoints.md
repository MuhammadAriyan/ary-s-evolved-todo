# FastAPI Chat Endpoints Skill

## Purpose
Implement stateless chat API endpoints with rate limiting, authentication, and proper error handling.

## Context7 Reference
- Library: `/tiangolo/fastapi`
- Query: "async endpoints middleware dependencies"

## Endpoint Patterns

### 1. Chat Router Structure
```python
# backend/app/api/v1/chat.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.chat import (
    SendMessageRequest,
    ChatResponse,
    ConversationResponse,
    ConversationListResponse,
)
from app.services.conversation_service import ConversationService
from app.services.ai.orchestrator import process_chat_message
from app.middleware.rate_limit import rate_limit

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])
```

### 2. Create Conversation Endpoint
```python
@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new conversation"""
    service = ConversationService(db)

    # Check conversation limit (max 100)
    count = await service.count_user_conversations(current_user.id)
    if count >= 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 100 conversations reached. Delete old conversations to continue."
        )

    conversation = await service.create_conversation(current_user.id)
    return ConversationResponse.from_orm(conversation)
```

### 3. List Conversations Endpoint
```python
@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List user's conversations"""
    service = ConversationService(db)
    conversations = await service.get_user_conversations(
        user_id=current_user.id,
        limit=min(limit, 100),  # Cap at 100
        offset=offset,
    )
    total = await service.count_user_conversations(current_user.id)

    return ConversationListResponse(
        conversations=conversations,
        total=total,
        limit=limit,
        offset=offset,
    )
```

### 4. Send Message Endpoint (Main Chat)
```python
@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=ChatResponse,
)
@rate_limit(requests=5, window=60)  # 5 messages per minute
async def send_message(
    conversation_id: str,
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a message and get AI response"""
    service = ConversationService(db)

    # Validate message length
    if len(request.content) > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message exceeds 1000 character limit"
        )

    # Verify conversation ownership
    conversation = await service.get_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id,
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Save user message
    user_message = await service.add_message(
        conversation_id=conversation_id,
        role="user",
        content=request.content,
    )

    # Get conversation history for context
    history = await service.get_conversation_history(conversation_id)

    # Process with AI (stateless)
    ai_response = await process_chat_message(
        user_id=current_user.id,
        message=request.content,
        conversation_history=history,
    )

    # Save assistant message
    assistant_message = await service.add_message(
        conversation_id=conversation_id,
        role="assistant",
        content=ai_response.content,
        agent_name=ai_response.agent_name,
        agent_icon=ai_response.agent_icon,
    )

    # Update conversation timestamp
    await service.update_conversation_timestamp(conversation_id)

    return ChatResponse(
        message=assistant_message,
        agent_name=ai_response.agent_name,
        agent_icon=ai_response.agent_icon,
    )
```

### 5. Delete Conversation Endpoint
```python
@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a conversation and all its messages"""
    service = ConversationService(db)

    # Verify ownership before delete
    conversation = await service.get_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id,
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    await service.delete_conversation(conversation_id)
    return {"success": True, "message": "Conversation deleted"}
```

### 6. Generate Title Endpoint
```python
@router.post("/conversations/{conversation_id}/title")
async def generate_title(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate AI title for conversation"""
    service = ConversationService(db)

    conversation = await service.get_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id,
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Get first few messages for context
    history = await service.get_conversation_history(
        conversation_id, limit=5
    )

    # Generate title with AI
    title = await generate_conversation_title(history)
    await service.update_conversation_title(conversation_id, title)

    return {"title": title}
```

### 7. Request/Response Schemas
```python
# backend/app/schemas/chat.py
from pydantic import BaseModel, Field
from datetime import datetime

class SendMessageRequest(BaseModel):
    content: str = Field(..., max_length=1000)
    language: str = Field(default="en-US", pattern="^(en-US|ur-PK)$")

class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    agent_name: str | None = None
    agent_icon: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    message: MessageResponse
    agent_name: str
    agent_icon: str

class ConversationResponse(BaseModel):
    id: str
    title: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ConversationListResponse(BaseModel):
    conversations: list[ConversationResponse]
    total: int
    limit: int
    offset: int
```

## Key Principles
- **Stateless**: No in-memory state, all in database
- **User Isolation**: Always verify ownership
- **Rate Limiting**: 5 messages per minute
- **Input Validation**: Pydantic schemas
- **Error Handling**: Proper HTTP status codes
