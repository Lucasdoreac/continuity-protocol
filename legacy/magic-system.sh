#!/bin/bash
# MAGIC SYSTEM - Auto input preservation + recovery + API integration

CONTINUITY_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY"
INPUT_LOG="$CONTINUITY_DIR/input-preservation.log"
MCP_SERVICE_DIR="$CONTINUITY_DIR/project-states/mcp-continuity-service"

detect_type() {
    local input_lower=$(echo "$1" | tr '[:upper:]' '[:lower:]')
    
    # Recovery triggers - mais abrangente
    if [[ "$input_lower" =~ (onde paramos|continue|status|contexto|projeto|trabalhamos|funcionou|quebrar|investigar|procure|produto continuity) ]]; then
        echo "RECOVERY"
    # Específico para projetos mencionados
    elif [[ "$input_lower" =~ (luaraujo|sabedoria-financeira|continuity|finn|premium-hub|mcp-continuity) ]]; then
        echo "RECOVERY" 
    # Input substantivo que precisa de contexto
    elif [[ ${#1} -gt 50 || "$input_lower" =~ (como|quando|porque|qual|fazer|implementar|corrigir|testar) ]]; then
        echo "RECOVERY"
    else
        echo "PRESERVE"
    fi
}

preserve() {
    echo "[$(date +%H%M%S)] INPUT: $1" >> "$INPUT_LOG"
    echo "--- PRESERVED ---" >> "$INPUT_LOG"
}

try_api_call() {
    # Priority 1: Try professional MCP-Continuity Service
    if curl -s -f http://localhost:8000/api/health >/dev/null 2>&1; then
        echo "🚀 USING PROFESSIONAL MCP-CONTINUITY SERVICE"
        cd "$MCP_SERVICE_DIR" && source venv/bin/activate && mcp-continuity process "$1" --format pretty 2>/dev/null || {
            echo "⚠️ MCP-Continuity CLI fallback error, using direct API"
            curl -s -X POST http://localhost:8000/api/process-input \
                -H "Content-Type: application/json" \
                -d "{\"input\": \"$1\"}" | head -c 500
        }
        return 0
    # Priority 2: Try legacy API if available  
    elif curl -s -f http://localhost:8000/health >/dev/null 2>&1; then
        echo "🔄 USING LEGACY API"
        cd "$MCP_SERVICE_DIR" && source venv/bin/activate && mcp-continuity process "$1" --format pretty
        return 0
    else
        return 1
    fi
}

magic() {
    local input="$1"
    
    case "$(detect_type "$input")" in
        "RECOVERY")
            echo "🎯 AUTO RECOVERY + CONTEXT LOADING"
            # Priority 1: Professional MCP-Continuity Service
            if ! try_api_call "$input"; then
                echo "📡 MCP-Continuity unavailable, using bash fallback"
                "$CONTINUITY_DIR/autonomous-recovery.sh"
            fi
            "$CONTINUITY_DIR/claude-mcp-guard.sh" status ;;
        "PRESERVE")
            echo "💾 PRESERVANDO + CONTEXTO VIA MCP-CONTINUITY"
            preserve "$input"
            # Always try professional service first
            if ! try_api_call "$input"; then
                echo "📡 MCP-Continuity unavailable, using basic preservation"
                "$CONTINUITY_DIR/auto-continuity.sh" luaraujo session-start
            fi
            "$CONTINUITY_DIR/claude-mcp-guard.sh" reset
            echo "✅ PRONTO PARA PROCESSAR" ;;
    esac
}

[[ $# -gt 0 ]] && magic "$*" || echo "USO: $0 \"input\""
