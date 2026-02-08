# Chat Diagnostic Guide

## Issue: Chat Not Working

This guide will help diagnose and fix the chat functionality issue.

## Quick Diagnostic Steps

### Step 1: Check Browser Console

1. Open http://localhost:3000/chat in your browser
2. Open DevTools (F12)
3. Go to Console tab
4. Look for any errors (red text)

**Common errors to look for:**
- "Failed to fetch"
- "401 Unauthorized"
- "Network error"
- "Cannot read property of undefined"

**Action**: Copy any error messages you see

---

### Step 2: Check Network Tab

1. In DevTools, go to Network tab
2. Refresh the page
3. Look for failed requests (red status codes)

**Check these endpoints:**
- `/api/auth/token` - Should return 200 OK
- `/api/v1/chat/conversations` - Should return 200 OK or 401

**Action**: Note which endpoints are failing

---

### Step 3: Test Chat API Manually

Open a new terminal and run:

```bash
# Get JWT token
TOKEN=$(curl -s http://localhost:3000/api/auth/token | jq -r '.token')
echo "Token: $TOKEN"

# Test conversations endpoint
curl -X GET "http://localhost:8000/api/v1/chat/conversations" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"

# Expected: {"conversations": [], "total": 0}
# If you see "Not authenticated", the token is invalid
```

---

### Step 4: Test Creating a Conversation

```bash
# Get token
TOKEN=$(curl -s http://localhost:3000/api/auth/token | jq -r '.token')

# Create conversation
curl -X POST "http://localhost:8000/api/v1/chat/conversations" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'

# Expected: {"id": "...", "user_id": "...", "title": "New Chat", ...}
```

---

### Step 5: Test Sending a Message

```bash
# Get token
TOKEN=$(curl -s http://localhost:3000/api/auth/token | jq -r '.token')

# Send message (creates conversation automatically)
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, can you help me?",
    "language_hint": "en"
  }'

# Expected: {"conversation_id": "...", "user_message": {...}, "assistant_message": {...}}
```

---

## Common Issues & Fixes

### Issue 1: "Not authenticated" Error

**Symptom**: API returns `{"detail": "Not authenticated"}`

**Cause**: JWT token is missing or invalid

**Fix**:
1. Check if you're logged in: http://localhost:3000/login
2. Verify BETTER_AUTH_URL in backend/.env matches frontend port (3000)
3. Restart backend if you changed .env

```bash
# Check backend .env
grep BETTER_AUTH_URL backend/.env

# Should be: BETTER_AUTH_URL=http://localhost:3000

# Restart backend
pkill -f "uvicorn"
cd backend
source venv/bin/activate
dapr run --app-id backend-api --app-port 8000 --app-protocol http --dapr-http-port 3500 -- uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

### Issue 2: Chat Page Loads But Nothing Happens

**Symptom**: Page loads, but no conversations appear, can't send messages

**Cause**: Frontend not fetching data or API calls failing silently

**Fix**:
1. Open browser console (F12)
2. Look for errors
3. Check Network tab for failed requests
4. Verify JWT token is being sent with requests

**Debug in browser console:**
```javascript
// Check if token is available
localStorage.getItem('better-auth.session_token')

// Check API client
fetch('http://localhost:8000/api/v1/chat/conversations', {
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN_HERE'
  }
}).then(r => r.json()).then(console.log)
```

---

### Issue 3: AI Not Responding

**Symptom**: Message sent but no response from AI

**Cause**: AI orchestrator not working or API key invalid

**Fix**:
1. Check AI_API_KEY in backend/.env
2. Verify OpenRouter API key is valid
3. Check backend logs for errors

```bash
# Check API key
grep AI_API_KEY backend/.env

# Test AI orchestrator
tail -f /tmp/claude/.../tasks/<backend-task-id>.output | grep -i "ai\|openai\|error"
```

---

### Issue 4: CORS Errors

**Symptom**: Browser console shows "CORS policy" errors

**Cause**: Backend CORS not configured for frontend origin

**Fix**:
1. Check CORS_ORIGINS in backend/.env
2. Should include http://localhost:3000

```bash
# Check CORS configuration
grep CORS_ORIGINS backend/.env

# Should be: CORS_ORIGINS=["http://localhost:3000"]
```

---

### Issue 5: Missing Dependencies

**Symptom**: Import errors or "module not found"

**Cause**: Frontend dependencies not installed

**Fix**:
```bash
cd frontend
npm install
npm run dev
```

---

## Step-by-Step Troubleshooting

### 1. Verify Backend is Running

```bash
curl http://localhost:8000/health | jq .
# Expected: {"status": "healthy", ...}
```

### 2. Verify Frontend is Running

```bash
curl -s http://localhost:3000 | head -20
# Should see HTML
```

### 3. Verify Authentication Works

```bash
# Get token
curl -s http://localhost:3000/api/auth/token | jq .
# Expected: {"token": "eyJ...", ...}
```

### 4. Verify Chat API is Registered

```bash
curl -s http://localhost:8000/docs | grep -o "chat" | head -5
# Should see "chat" multiple times
```

### 5. Test Complete Flow

```bash
# 1. Get token
TOKEN=$(curl -s http://localhost:3000/api/auth/token | jq -r '.token')

# 2. List conversations
curl -X GET "http://localhost:8000/api/v1/chat/conversations" \
  -H "Authorization: Bearer $TOKEN" | jq .

# 3. Send message
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}' | jq .
```

---

## What to Report

If chat still doesn't work after trying these steps, please provide:

1. **Browser console errors** (screenshot or copy-paste)
2. **Network tab failed requests** (which endpoints are failing)
3. **Backend logs** (any errors from backend)
4. **Test results** (output from manual API tests above)

---

## Quick Fix Commands

### Restart Everything

```bash
# Stop all services
pkill -f "dapr run"
pkill -f "uvicorn"
pkill -f "next"

# Start infrastructure
cd infrastructure
docker compose -f docker-compose.dev.yml up -d

# Start backend
cd ../backend
source venv/bin/activate
dapr run --app-id backend-api --app-port 8000 --app-protocol http --dapr-http-port 3500 -- uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &

# Start frontend
cd ../frontend
npm run dev &
```

### Check All Services

```bash
# Backend
curl http://localhost:8000/health | jq .

# Frontend
curl -s http://localhost:3000 | head -5

# Auth
curl -s http://localhost:3000/api/auth/token | jq .

# Chat API
TOKEN=$(curl -s http://localhost:3000/api/auth/token | jq -r '.token')
curl -X GET "http://localhost:8000/api/v1/chat/conversations" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

---

## Expected Behavior

When chat is working correctly:

1. **Page loads**: http://localhost:3000/chat shows chat interface
2. **Conversations load**: Left sidebar shows conversation list (may be empty)
3. **Can create conversation**: Click "New Chat" creates a conversation
4. **Can send message**: Type message and press Enter
5. **AI responds**: Assistant message appears within 5-10 seconds
6. **Streaming works**: Response appears word-by-word (streaming)

---

## Next Steps

1. Follow diagnostic steps above
2. Note which step fails
3. Apply the corresponding fix
4. Test again
5. Report results if still not working
