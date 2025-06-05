#!/bin/bash
# PROJECT FINDER OPTIMIZED - Using MCP-Continuity Service
# Busca projetos ativos com máxima eficiência e mínimos tokens

CONTINUITY_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY"
MCP_SERVICE_DIR="$CONTINUITY_DIR/project-states/mcp-continuity-service"

get_active_projects_mcp() {
    echo "🔍 BUSCANDO PROJETOS VIA MCP-CONTINUITY..."
    
    # Try professional service first
    if curl -s -f http://localhost:8000/api/health >/dev/null 2>&1; then
        cd "$MCP_SERVICE_DIR" && source venv/bin/activate
        
        echo "🚀 MCP-Continuity Service ATIVO!"
        
        # Get project context via API
        curl -s -X POST http://localhost:8000/api/process-input \
            -H "Content-Type: application/json" \
            -d '{"user_input": "liste projetos ativos", "session_id": "finder-session"}' | \
            python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f'📊 Resposta: {data.get(\"type\", \"unknown\")}')
    if data.get('content'):
        print(f'📋 Contexto: {data[\"content\"][:200]}...')
except:
    print('⚠️ Processando via CLI...')
            " 2>/dev/null
        
        # Also try CLI command
        mcp-continuity process "projetos ativos status" --format compact 2>/dev/null || echo "CLI indisponível"
        return 0
    fi
    
    return 1
}

get_active_projects_legacy() {
    echo "📂 BUSCA LEGADA DE PROJETOS..."
    
    # Efficient project detection from states
    for state in "$CONTINUITY_DIR/project-states"/*.json; do
        if [[ -f "$state" ]]; then
            project=$(basename "$state" .json)
            last_update=$(stat -f %m "$state" 2>/dev/null || echo "0")
            current_time=$(date +%s)
            age=$((current_time - last_update))
            
            # Only active projects (updated in last 24h)
            if [[ $age -lt 86400 ]]; then
                echo "✅ $project ($(($age/3600))h ago)"
            fi
        fi
    done
}

get_current_context_efficient() {
    echo "📱 CAPTURANDO CONTEXTO EFICIENTE..."
    
    # Essential context only - minimize tokens
    echo "🖥️ PROCESSOS: $(ps aux | grep -E '(expo|npm|node)' | grep -v grep | wc -l | tr -d ' ') Node/Expo ativos"
    echo "🌐 PORTAS: $(lsof -i :8000,8001,8081,8501 2>/dev/null | grep LISTEN | wc -l | tr -d ' ') serviços rodando"
    echo "📁 FINDER: $(osascript -e 'tell app "Finder" to get the name of the front window' 2>/dev/null || echo "N/A")"
}

main() {
    echo "🎯 PROJECT FINDER - OPTIMIZED FOR TOKEN EFFICIENCY"
    echo "================================================"
    
    # Try MCP-Continuity first, fallback to legacy
    if ! get_active_projects_mcp; then
        get_active_projects_legacy
    fi
    
    echo ""
    get_current_context_efficient
    
    echo ""
    echo "🔗 ACESSO RÁPIDO:"
    echo "   • MCP-Continuity UI: http://localhost:8501"
    echo "   • API Docs: http://localhost:8000/docs"  
    echo "   • Sabedoria AI: http://localhost:8081"
}

[[ "${BASH_SOURCE[0]}" == "${0}" ]] && main "$@"
