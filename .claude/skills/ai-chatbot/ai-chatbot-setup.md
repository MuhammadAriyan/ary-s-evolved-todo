# AI Chatbot Setup Skill

## Purpose
Configure OpenAI Agents SDK with custom AI provider (base_url, api_key) for the AI Todo Chatbot.

## Context7 Reference
- Library: `/openai/openai-agents-python`
- Query: "Agent configuration with custom client"

## Configuration Pattern

### 1. Environment Variables
```bash
# .env
AI_API_KEY=your-api-key-here
AI_BASE_URL=https://api.openai.com/v1  # Or custom provider
AI_MODEL=gpt-4o-mini
```

### 2. Settings Configuration
```python
# backend/app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ai_api_key: str
    ai_base_url: str = "https://api.openai.com/v1"
    ai_model: str = "gpt-4o-mini"

    class Config:
        env_file = ".env"

settings = Settings()
```

### 3. Custom Client Setup
```python
# backend/app/services/ai/config.py
from openai import AsyncOpenAI
from agents import set_default_openai_client
from app.core.config import settings

# Create custom client with user's API key and base URL
external_client = AsyncOpenAI(
    api_key=settings.ai_api_key,
    base_url=settings.ai_base_url,
)

# Set as default for all agents
set_default_openai_client(external_client)

# Model configuration for agents
MODEL_CONFIG = {
    "model": settings.ai_model,
    "temperature": 0.7,
    "max_tokens": 1000,
}
```

### 4. Agent Creation Pattern
```python
from agents import Agent, Runner
from app.services.ai.config import MODEL_CONFIG

# Create agent with custom model config
orchestrator = Agent(
    name="Aren",
    instructions="You are the main orchestrator...",
    model=MODEL_CONFIG["model"],
)

# Run agent
async def process_message(message: str, history: list):
    runner = Runner(agent=orchestrator)
    result = await runner.run(
        messages=history + [{"role": "user", "content": message}]
    )
    return result
```

### 5. RunConfig for Advanced Settings
```python
from agents.run import RunConfig

run_config = RunConfig(
    model=settings.ai_model,
    model_provider="openai",  # or custom provider
    tracing_disabled=True,  # Disable if not using OpenAI tracing
)
```

## Key Points
- Always use environment variables for API keys
- Set custom client BEFORE creating agents
- Use `set_default_openai_client()` for global configuration
- RunConfig allows per-run customization
