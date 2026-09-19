#!/usr/bin/env bash
set -e
python -m mcp_server.server &
MCP_PID=$!
trap 'kill $MCP_PID' EXIT
uvicorn backend.app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
