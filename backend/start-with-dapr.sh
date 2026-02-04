#!/bin/bash
cd /home/ary/Dev/abc/Ary-s-Evolutioned-Todo/backend
source venv/bin/activate

dapr run \
  --app-id backend-api \
  --app-port 8000 \
  --dapr-http-port 3500 \
  --dapr-grpc-port 50001 \
  --components-path ../infrastructure/dapr \
  -- uvicorn app.main:app --host 0.0.0.0 --port 8000
