# Chat Issue Diagnosis & Fix

## Issue Summary

The chat is not working. Based on initial diagnostics:

✅ **Backend API**: Healthy and running (port 8000)
✅ **Frontend**: Running (port 3000)
✅ **AI API Key**: Configured in backend/.env
❌ **User Session**: Returning null (user might not be logged in)

---

## Root Cause

The most likely issue is that **you're not logged in** or your **session has expired**.

---

## Quick Fix (Try This First)

### Step 1: Log In

1. Open http://localhost:3000/login in your browser
2. Log in with your credentials
3. After successful login, you should be redirected to /todo
4. Now try accessing http://localhost:3000/chat

### Step 2: Verify You're Logged In

Open browser console (F12) and run:
```javascript
// Check session
fetch('/api/auth/get-session')
  .then(r => r.json())
  .then(data => {
    console.log('Session:', data)
    console.log('User ID:', data.user?.id)
    console.log('Email:', data.user?.email)
  })
```

**Expected output:**
```json
{
  "user": {
    "id": "yVw2p0aj337xPxsTMqFASoh5TlxHU5oK",
    "email": "your@email.com",
    "name": "Your Name"
  },
  "session": { ... }
}
```

If you see `"user": null`, you're not logged in.

---

## Manual Testing (After Logging In)

### Test 1: Get JWT Token

```bash
curl -s http://localhost:3000/api/auth/token | jq .
```

**Expected:**
```json
{
  "token": "eyJhbGciOiJFZERTQSIsImtpZCI6IjFxN2Y2elRtZ0gwM0hZa0ZnbXlURmY0Y0hVUTRMbk5MIn0..."
}
```

### Test 2: List Conversations

```bash
TOKEN=$(curl -s http://localhost:3000/api/auth/token | jq -r '.token')
curl -X GET "http://localhost:8000/api/v1/chat/conversations" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

**Expected:**
```json
{
  "conversations": [],
  "total": 0
}
```

### Test 3: Send a Message

```bash
TOKEN=$(curl -s http://localhost:3000/api/auth/token | jq -r '.token')
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, can you help me create a task?",
    "language_hint": "en"
  }' | jq .
```

**Expected:**
```json
{
  "conversation_id": "...",
  "user_message": {
    "id": "...",
    "role": "user",
    "content": "Hello, can you help me create a task?"
  },
  "assistant_message": {
    "id": "...",
    "role": "assistant",
    "content": "Of course! I'd be happy to help you create a task...",
    "agent_name": "Aren",
    "agent_icon": "🤖"
  }
}
```

---

## Browser Testing

### Step 1: Open Chat Page

1. Make sure you're logged in
2. Go to http://localhost:3000/chat
3. Open DevTools (F12) → Console tab

### Step 2: Check for Errors

Look for any red error messages in the console. Common errors:

**Error: "Failed to fetch"**
- **Cause**: Backend not running or CORS issue
- **Fix**: Restart backend, check CORS_ORIGINS in backend/.env

**Error: "401 Unauthorized"**
- **Cause**: Not logged in or token expired
- **Fix**: Log in again

**Error: "Cannot read property of undefined"**
- **Cause**: Frontend code issue
- **Fix**: Check browser console for stack trace

### Step 3: Test in Browser Console

```javascript
// Test chat API
const testChat = async () => {
  try {
    // Get token
    const tokenRes = await fetch('/api/auth/token')
    const tokenData = await tokenRes.json()
    console.log('Token:', tokenData.token?.substring(0, 50) + '...')

    // List conversations
    const convRes = await fetch('http://localhost:8000/api/v1/chat/conversations', {
      headers: {
        'Authorization': `Bearer ${tokenData.token}`
      }
    })
    const convData = await convRes.json()
    console.log('Conversations:', convData)

    // Send message
    const msgRes = await fetch('http://localhost:8000/api/v1/chat', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${tokenData.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: 'Hello!',
        language_hint: 'en'
      })
    })
    const msgData = await msgRes.json()
    console.log('Response:', msgData)
  } catch (error) {
    console.error('Error:', error)
  }
}

testChat()
```

---

## Common Issues & Solutions

### Issue 1: Not Logged In

**Symptom**: Session returns null, chat page shows nothing

**Solution**:
1. Go to http://localhost:3000/login
2. Log in with your credentials
3. Try chat again

### Issue 2: Session Expired

**Symptom**: Was working before, now returns 401

**Solution**:
1. Log out: http://localhost:3000/api/auth/sign-out
2. Log in again: http://localhost:3000/login

### Issue 3: Backend Not Running

**Symptom**: "Failed to fetch" or "Network error"

**Solution**:
```bash
# Check backend
curl http://localhost:8000/health

# If not running, restart
cd backend
source venv/bin/activate
dapr run --app-id backend-api --app-port 8000 --app-protocol http --dapr-http-port 3500 -- uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Issue 4: CORS Error

**Symptom**: Browser console shows "CORS policy" error

**Solution**:
```bash
# Check CORS configuration
grep CORS_ORIGINS backend/.env

# Should be: CORS_ORIGINS=["http://localhost:3000"]

# If wrong, fix it and restart backend
```

### Issue 5: AI Not Responding

**Symptom**: Message sent but no response

**Solution**:
1. Check AI_API_KEY in backend/.env
2. Check backend logs for errors
3. Verify OpenRouter API key is valid

```bash
# Check API key
grep AI_API_KEY backend/.env

# Test AI orchestrator
tail -100 /tmp/claude/.../tasks/<backend-task-id>.output | grep -i "error"
```

---

## Expected Behavior

When chat is working correctly:

1. ✅ You're logged in (session shows user data)
2. ✅ Chat page loads at http://localhost:3000/chat
3. ✅ Left sidebar shows "New Chat" button
4. ✅ Can click "New Chat" to create conversation
5. ✅ Can type message and press Enter
6. ✅ AI responds within 5-10 seconds
7. ✅ Response appears word-by-word (streaming)

---

## Debugging Checklist

- [ ] I'm logged in (verified in browser console)
- [ ] Backend is running (curl http://localhost:8000/health works)
- [ ] Frontend is running (http://localhost:3000 loads)
- [ ] JWT token is available (curl http://localhost:3000/api/auth/token works)
- [ ] Chat API responds (curl with token to /api/v1/chat/conversations works)
- [ ] No CORS errors in browser console
- [ ] No 401 errors in browser console
- [ ] AI_API_KEY is configured in backend/.env

---

## Next Steps

1. **Log in** at http://localhost:3000/login
2. **Open chat** at http://localhost:3000/chat
3. **Check browser console** for errors (F12)
4. **Try sending a message**
5. **Report results**: What happens? Any errors?

---

## If Still Not Working

Please provide:

1. **Screenshot of browser console** (F12 → Console tab)
2. **Screenshot of Network tab** (F12 → Network tab, filter by "chat")
3. **Output of these commands**:
   ```bash
   curl -s http://localhost:3000/api/auth/get-session | jq .
   curl -s http://localhost:8000/health | jq .
   ```

This will help me diagnose the exact issue.
