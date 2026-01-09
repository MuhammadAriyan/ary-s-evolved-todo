---
description: Start both frontend and backend development servers
---

## Dev Servers Startup

Start both the backend and frontend development servers for local development.

### Instructions

1. **Kill any existing processes** on ports 8000 and 3004:
   ```bash
   fuser -k 8000/tcp 2>/dev/null
   fuser -k 3004/tcp 2>/dev/null
   ```

2. **Start the backend server** (in background):
   ```bash
   cd /home/ary/Dev/abc/Ary-s-Evolutioned-Todo && source .venv/bin/activate && cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Start the frontend server** (in background):
   ```bash
   cd /home/ary/Dev/abc/Ary-s-Evolutioned-Todo/frontend && PORT=3004 npm run dev
   ```

4. **Verify both servers are running**:
   - Backend: http://localhost:8000
   - Frontend: http://localhost:3004

5. **Report status** to the user with the URLs.

### Server Details

| Service  | Port | URL                    |
|----------|------|------------------------|
| Backend  | 8000 | http://localhost:8000  |
| Frontend | 3004 | http://localhost:3004  |
