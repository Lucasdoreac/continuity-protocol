#!/bin/bash
# MCP Continuity Service - Complete Startup

echo "🚀 Starting MCP Continuity Service..."

# Start API in background
source venv/bin/activate
mcp-continuity start &
API_PID=$!

# Wait for API to be ready
sleep 3

# Start UI in background  
mcp-continuity ui &
UI_PID=$!

echo "✅ Services started:"
echo "   📡 API: http://localhost:8000"
echo "   🎨 UI:  http://localhost:8501"
echo "   🔧 CLI: mcp-continuity process 'your input'"
echo ""
echo "To stop: kill $API_PID $UI_PID"
echo "PIDs saved to .service_pids"
echo "$API_PID $UI_PID" > .service_pids
