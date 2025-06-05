#!/bin/bash
# MCP GUARD - Integração automática do monitor com ações MCP

CONTINUITY_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY"
MONITOR="$CONTINUITY_DIR/mcp-self-monitor.sh"

# Inicializar monitor
if [[ ! -f "$CONTINUITY_DIR/mcp-monitor/.monitor_active" ]]; then
    "$MONITOR" start
    touch "$CONTINUITY_DIR/mcp-monitor/.monitor_active"
fi

auto_monitor() {
    local action="$1" data="$2" source="${3:-user}"
    
    "$MONITOR" monitor "$action" "$data" "$source"
    
    if [[ -f "$CONTINUITY_DIR/mcp-monitor/CRITICAL_ALERT.txt" ]]; then
        echo "🚨🚨🚨 ALERTA CRÍTICO MCP 🚨🚨🚨"
        cat "$CONTINUITY_DIR/mcp-monitor/CRITICAL_ALERT.txt"
        echo "🛡️ REVISAR: últimas ações, fontes externas, autorizações"
        return 1
    fi
    return 0
}

pre_mcp_check() {
    local action="$1" target="$2" context="$3"
    echo "🛡️ Verificando: $action"
    
    auto_monitor "PRE_CHECK" "$action -> $target" "$context"
    
    if [[ $? -ne 0 ]]; then
        echo "❌ Ação bloqueada"
        return 1
    fi
    
    echo "✅ Ação autorizada"
    return 0
}

guard_status() {
    echo "🛡️ MCP GUARD STATUS:"
    "$MONITOR" status
    [[ -f "$CONTINUITY_DIR/mcp-monitor/CRITICAL_ALERT.txt" ]] && echo "🚨 ALERTA ATIVO" && cat "$CONTINUITY_DIR/mcp-monitor/CRITICAL_ALERT.txt"
}

case "$1" in
    monitor) auto_monitor "$2" "$3" "$4" ;;
    check) pre_mcp_check "$2" "$3" "$4" ;;
    status) guard_status ;;
    reset) 
        rm -f "$CONTINUITY_DIR/mcp-monitor/CRITICAL_ALERT.txt" "$CONTINUITY_DIR/mcp-monitor/.monitor_active"
        echo "🔄 Monitor resetado"
        ;;
    *) 
        echo "USO: $0 {monitor|check|status|reset}"
        echo "EXEMPLOS:"
        echo "  $0 check read_file repo/file.js 'source context'"
        echo "  $0 monitor create_pull_request user/repo 'PR content'"
        echo "  $0 status"
        ;;
esac
