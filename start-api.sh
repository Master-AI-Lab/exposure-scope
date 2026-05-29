#!/bin/bash
# 🐺 exposure-scope — HUNTER API Server Launcher
# Run this on the VPS to start the backend API server.
# The Vercel frontend proxies through /api/scan to this server.

echo "🔍 Starting exposure-scope API Server..."
echo "   Port: 8115"
echo "   Tools: SpiderFoot, Sherlock, holehe, theHarvester, TruffleHog"
echo ""

cd "$(dirname "$0")"

# Kill any existing instance
pkill -f "api_server.py" 2>/dev/null || true
sleep 1

# Ensure fastapi/uvicorn installed
pip3 install --break-system-packages fastapi uvicorn 2>/dev/null | tail -1

# Start server
python3 backend/api_server.py
