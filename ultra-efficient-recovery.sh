#!/bin/bash
# ULTRA-EFFICIENT CONTEXT RECOVERY - Minimal Tokens Maximum Context
# Para uso em próximos chats com gastos mínimos de tokens

CONTINUITY_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY"
MCP_SERVICE_DIR="$CONTINUITY_DIR/project-states/mcp-continuity-service"

# Ultra-compact context retrieval
get_session_summary() {
    local compact_file="$CONTINUITY_DIR/session-context-compact.json"
    
    if [[ -f "$compact_file" ]]; then
        echo "📋 CONTEXTO COMPACTO CARREGADO:"
        python3 -c "
import json
with open('$compact_file') as f:
    data = json.load(f)
    print(f'🕐 {data[\"timestamp\"][:16]}')
    for achievement in data['achievements']:
        print(f'  {achievement}')
    print('')
    print('🌐 SERVIÇOS:')
    for service, status in data['active_services'].items():
        print(f'  • {service}: {status}')
    print('')
    print('🎯 PRÓXIMAS AÇÕES:')
    for action, desc in data['immediate_actions'].items():
        print(f'  • {action}: {desc}')
" 2>/dev/null || echo "⚠️ Contexto compacto indisponível"
    fi
}

# Quick project status via MCP-Continuity
get_quick_status() {
    if curl -s -f http://localhost:8000/api/health >/dev/null 2>&1; then
        echo "🚀 MCP-CONTINUITY ATIVO - Processamento inteligente disponível"
        
        # Quick status call
        curl -s -X POST http://localhost:8000/api/process-input \
            -H "Content-Type: application/json" \
            -d '{"user_input": "status projetos", "session_id": "quick-recovery"}' | \
            python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(f'📊 MCP Response: {data.get(\"type\", \"N/A\")}')
except:
    pass
" 2>/dev/null
    else
        echo "⚠️ MCP-Continuity indisponível - usando fallback"
        echo "📂 Projetos detectados:"
        ls -1 "$CONTINUITY_DIR/project-states"/*.json 2>/dev/null | \
            xargs -I {} basename {} .json | \
            head -4 | \
            sed 's/^/  • /'
    fi
}

# Minimal system info
get_minimal_context() {
    echo "💻 SISTEMA: $(ps aux | grep -E '(expo|node)' | grep -v grep | wc -l | tr -d ' ') processos, $(lsof -i :8000,8081,8501 2>/dev/null | grep LISTEN | wc -l | tr -d ' ') serviços"
}

# Main ultra-efficient recovery
main() {
    echo "⚡ ULTRA-EFFICIENT CONTEXT RECOVERY"
    echo "=================================="
    
    get_session_summary
    echo ""
    get_quick_status  
    echo ""
    get_minimal_context
    
    echo ""
    echo "🎯 COMANDOS RÁPIDOS:"
    echo "  • Magic: /Users/lucascardoso/apps/MCP/CONTINUITY/magic-system.sh"
    echo "  • MCP UI: http://localhost:8501"
    echo "  • API: http://localhost:8000/docs"
}

[[ "${BASH_SOURCE[0]}" == "${0}" ]] && main "$@"
