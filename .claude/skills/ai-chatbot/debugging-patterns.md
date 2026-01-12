# Debugging Patterns Skill

## Purpose
Diagnose and resolve issues in AI agent behavior, MCP tool execution, and chat flow for the AI Todo Chatbot.

## Common Issues & Solutions

### 1. Agent Not Responding

**Symptoms**: Chat returns empty or error response

**Diagnostic Steps**:
```python
# 1. Check AI API connectivity
async def check_ai_health():
    try:
        response = await external_client.models.list()
        print(f"✅ AI API connected, latency: {response.latency}ms")
        return True
    except Exception as e:
        print(f"❌ AI API error: {e}")
        return False

# 2. Verify API key
import os
api_key = os.getenv("AI_API_KEY")
if not api_key:
    print("❌ AI_API_KEY not set")
elif len(api_key) < 20:
    print("❌ AI_API_KEY looks invalid")
else:
    print(f"✅ AI_API_KEY set: {api_key[:10]}...")

# 3. Check base URL
base_url = os.getenv("AI_BASE_URL")
print(f"Base URL: {base_url}")
```

**Common Fixes**:
- Set `AI_API_KEY` in `.env`
- Verify `AI_BASE_URL` is correct
- Check API rate limits on provider

### 2. Wrong Agent Responding

**Symptoms**: English message routed to Urdu agent or vice versa

**Diagnostic Steps**:
```python
# Add logging to orchestrator
import logging
logger = logging.getLogger("orchestrator")

async def process(self, message: str):
    language = await self._detect_language(message)
    logger.info(f"Detected language: {language} for message: {message[:50]}...")

    if language == "ur":
        logger.info("Routing to Riven (Urdu)")
        return await self.urdu_agent.process(message)
    else:
        logger.info("Routing to Miyu (English)")
        return await self.english_agent.process(message)
```

**Common Fixes**:
- Improve language detection prompt
- Add explicit language hints in user message
- Check for mixed-language edge cases

### 3. MCP Tool Failures

**Symptoms**: Tool returns error or unexpected result

**Diagnostic Steps**:
```python
# 1. Validate tool inputs
def validate_tool_call(tool_name: str, params: dict):
    required = {
        "add_task": ["user_id", "title"],
        "list_tasks": ["user_id"],
        "complete_task": ["user_id", "task_id"],
        # ...
    }

    missing = [p for p in required.get(tool_name, []) if p not in params]
    if missing:
        print(f"❌ Missing params for {tool_name}: {missing}")
        return False

    if "user_id" not in params:
        print("❌ CRITICAL: user_id missing - isolation violation!")
        return False

    return True

# 2. Check database connection
async def check_db_health():
    try:
        async with get_session() as session:
            await session.execute("SELECT 1")
        print("✅ Database connected")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

# 3. Log tool execution
@function_tool
async def add_task(user_id: str, title: str, **kwargs):
    logger.info(f"add_task called: user_id={user_id}, title={title}")
    try:
        result = await _add_task_impl(user_id, title, **kwargs)
        logger.info(f"add_task success: {result}")
        return result
    except Exception as e:
        logger.error(f"add_task failed: {e}")
        return {"success": False, "error": str(e)}
```

**Common Fixes**:
- Ensure `user_id` is always passed
- Check database connection string
- Verify SQLModel migrations ran

### 4. Rate Limiting Issues

**Symptoms**: 429 errors, messages blocked

**Diagnostic Steps**:
```python
# Check rate limiter state
class RateLimiter:
    async def debug_state(self, user_id: str):
        if user_id not in self.cache:
            print(f"User {user_id}: No requests recorded")
            return

        requests = self.cache[user_id]
        print(f"User {user_id}: {len(requests)} requests in window")
        for i, ts in enumerate(requests):
            print(f"  {i+1}. {ts}")

# Add to endpoint for debugging
@router.get("/debug/rate-limit/{user_id}")
async def debug_rate_limit(user_id: str):
    if not settings.debug_mode:
        raise HTTPException(404)
    return await rate_limiter.debug_state(user_id)
```

**Common Fixes**:
- Verify rate limit config (5 req/60s)
- Check user_id extraction from JWT
- Clear rate limiter cache if stuck

### 5. Conversation State Issues

**Symptoms**: Agent loses context, repeats questions

**Diagnostic Steps**:
```python
# Log conversation history
async def process_chat_message(user_id, message, history):
    logger.info(f"Processing message for user {user_id}")
    logger.info(f"History length: {len(history)} messages")
    for i, msg in enumerate(history[-5:]):  # Last 5
        logger.info(f"  [{i}] {msg['role']}: {msg['content'][:50]}...")

    # Check history format
    for msg in history:
        if "role" not in msg or "content" not in msg:
            logger.error(f"Invalid message format: {msg}")
```

**Common Fixes**:
- Ensure messages saved to DB before response
- Check conversation_id is correct
- Verify message ordering (by created_at)

### 6. Debug Logging Configuration
```python
# backend/app/core/logging.py
import logging
import sys

def setup_debug_logging():
    """Enable verbose logging for debugging"""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Enable specific loggers
    loggers = [
        "orchestrator",
        "language_agents",
        "task_agents",
        "mcp_tools",
        "rate_limiter",
        "chat_api",
    ]
    for name in loggers:
        logging.getLogger(name).setLevel(logging.DEBUG)

# Enable in development
if settings.debug_mode:
    setup_debug_logging()
```

### 7. Health Check Endpoint
```python
@router.get("/health")
async def health_check():
    """Comprehensive health check"""
    checks = {
        "ai_api": await check_ai_health(),
        "database": await check_db_health(),
        "agents": check_agents_loaded(),
    }

    all_healthy = all(checks.values())
    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "checks": checks,
    }
```

## Debugging Workflow
1. **Reproduce** - Get exact steps to trigger issue
2. **Enable Logging** - Turn on debug logs
3. **Trace Flow** - Follow message through agents
4. **Isolate** - Find which component fails
5. **Fix** - Apply targeted fix
6. **Verify** - Confirm issue resolved
7. **Test** - Add test to prevent regression
