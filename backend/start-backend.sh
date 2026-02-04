#!/bin/bash
cd /home/ary/Dev/abc/Ary-s-Evolutioned-Todo/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
