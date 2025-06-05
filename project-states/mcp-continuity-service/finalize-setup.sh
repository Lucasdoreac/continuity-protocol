#!/bin/bash
# FINALIZATION SCRIPT - Complete MCP Continuity Service Setup

echo "🎯 FINALIZING MCP-CONTINUITY SERVICE"
echo "======================================"

cd /Users/lucascardoso/apps/MCP/CONTINUITY/project-states/mcp-continuity-service

# 1. Update configuration for LLM provider (use Anthropic instead of Ollama)
echo "🔧 Configuring LLM provider..."
cat > config/default.json << 'EOF'
{
  "llm": {
    "provider": "anthropic",
    "model": "claude-3-sonnet-20240229",
    "api_key_env": "ANTHROPIC_API_KEY",
    "fallback_provider": "openai",
    "fallback_model": "gpt-3.5-turbo"
  },
  "continuity": {
    "detection_patterns": [
      "onde paramos",
      "continue",
      "status",
      "where did we leave off",
      "resume"
    ],
    "context_capture": {
      "applications": true,
      "documents": true,
      "notes": true,
      "calendar": true
    }
  },
  "api": {
    "host": "127.0.0.1",
    "port": 8000
  },
  "ui": {
    "port": 8501
  }
}
EOF

# 2. Create startup script
echo "🚀 Creating startup script..."
cat > start-service.sh << 'EOF'
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
EOF

chmod +x start-service.sh

# 3. Create service management script
echo "⚙️ Creating service manager..."
cat > manage-service.sh << 'EOF'
#!/bin/bash
# MCP Continuity Service Manager

case "$1" in
  start)
    echo "🚀 Starting services..."
    ./start-service.sh
    ;;
  stop)
    echo "🛑 Stopping services..."
    if [ -f .service_pids ]; then
      kill $(cat .service_pids) 2>/dev/null
      rm .service_pids
      echo "✅ Services stopped"
    else
      echo "⚠️ No running services found"
    fi
    ;;
  status)
    echo "📊 Service status:"
    curl -s http://localhost:8000/api/health | jq . 2>/dev/null || echo "❌ API not responding"
    lsof -i :8501 >/dev/null && echo "✅ UI running on :8501" || echo "❌ UI not running"
    ;;
  restart)
    $0 stop
    sleep 2
    $0 start
    ;;
  *)
    echo "Usage: $0 {start|stop|status|restart}"
    exit 1
    ;;
esac
EOF

chmod +x manage-service.sh

echo ""
echo "🎉 MCP CONTINUITY SERVICE FINALIZED!"
echo "====================================="
echo ""
echo "📋 Available commands:"
echo "   ./manage-service.sh start   - Start all services"
echo "   ./manage-service.sh stop    - Stop all services"  
echo "   ./manage-service.sh status  - Check service status"
echo "   ./manage-service.sh restart - Restart services"
echo ""
echo "🔧 Direct usage:"
echo "   mcp-continuity process 'onde paramos?'"
echo "   mcp-continuity start"
echo "   mcp-continuity ui"
echo ""
echo "🌐 Access points:"
echo "   API: http://localhost:8000/docs"
echo "   UI:  http://localhost:8501"
echo ""
echo "✅ Integration with current system: ACTIVE"
echo "📡 magic-system.sh will automatically use API when available"
echo "🛡️ Fallback to bash scripts if API unavailable"
