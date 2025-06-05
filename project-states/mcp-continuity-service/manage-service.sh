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
