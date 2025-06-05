#!/bin/bash
# MCP SELF-MONITOR - Auto-Monitoramento de Segurança

MONITOR_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY/mcp-monitor"
LOG="$MONITOR_DIR/session-$(date +%H%M%S).log"
mkdir -p "$MONITOR_DIR"

# Estado usando arquivos (compatível com todos os shells)
REPOS_FILE="$MONITOR_DIR/.repos"
ALERTS_FILE="$MONITOR_DIR/.alerts"
SCORE_FILE="$MONITOR_DIR/.score"

# Inicializar arquivos de estado
[[ ! -f "$SCORE_FILE" ]] && echo "0" > "$SCORE_FILE"
[[ ! -f "$REPOS_FILE" ]] && touch "$REPOS_FILE"
[[ ! -f "$ALERTS_FILE" ]] && touch "$ALERTS_FILE"

get_score() { cat "$SCORE_FILE" 2>/dev/null || echo "0"; }
add_score() { echo "$(($(get_score) + $1))" > "$SCORE_FILE"; }
get_repo_count() { wc -l < "$REPOS_FILE" 2>/dev/null || echo "0"; }
get_alert_count() { wc -l < "$ALERTS_FILE" 2>/dev/null || echo "0"; }

log_action() { echo "[$(date +%H:%M:%S)] $1" >> "$LOG"; }

check_repo() {
    local repo="$1"
    if [[ -n "$repo" ]] && ! grep -q "^$repo$" "$REPOS_FILE" 2>/dev/null; then
        echo "$repo" >> "$REPOS_FILE"
        if [[ $(get_repo_count) -gt 1 ]]; then
            echo "🚨 Multi-repo: $repo" >> "$ALERTS_FILE"
            add_score 50
        fi
    fi
}

check_suspicious() {
    case "$1" in
        *"create_pull_request"*|*"write_file"*|*"execute_command"*)
            echo "⚠️ Suspeito: $1" >> "$ALERTS_FILE"
            add_score 25 ;;
    esac
}

check_injection() {
    if echo "$1" | grep -qi "ignore previous\|access private\|leak"; then
        echo "🚨 Injection" >> "$ALERTS_FILE"
        add_score 75
    fi
}

monitor() {
    log_action "$1: $2"
    local repo=$(echo "$2" | grep -oE "[^/]+/[^/]+" | head -1)
    [[ -n "$repo" ]] && check_repo "$repo"
    check_suspicious "$1"
    [[ -n "$3" ]] && check_injection "$3"
    
    local current_score=$(get_score)
    if [[ $current_score -gt 100 ]]; then
        echo "🚨 ALERTA CRÍTICO: Score=$current_score Repos=$(get_repo_count) Alertas=$(get_alert_count)"
        cat "$ALERTS_FILE" 2>/dev/null
        
        # Salvar alerta crítico
        echo "$(date): Score=$current_score" > "$MONITOR_DIR/CRITICAL_ALERT.txt"
        cat "$ALERTS_FILE" >> "$MONITOR_DIR/CRITICAL_ALERT.txt" 2>/dev/null
    fi
}

status() {
    echo "📊 MCP Monitor Status:"
    echo "   Score: $(get_score)/100"
    echo "   Repos: $(get_repo_count)/1"
    echo "   Alertas: $(get_alert_count)"
    
    if [[ $(get_alert_count) -gt 0 ]]; then
        echo "   Alertas ativos:"
        cat "$ALERTS_FILE" | sed 's/^/     /'
    fi
}

reset_monitor() {
    echo "0" > "$SCORE_FILE"
    > "$REPOS_FILE"
    > "$ALERTS_FILE"
    rm -f "$MONITOR_DIR/CRITICAL_ALERT.txt"
    echo "🔄 Monitor resetado"
}

case "$1" in
    monitor) monitor "$2" "$3" "$4" ;;
    status) status ;;
    start) echo "🛡️ MCP Monitor iniciado: $LOG" ;;
    reset) reset_monitor ;;
    *) echo "USO: $0 {start|monitor <acao> <dados> [fonte]|status|reset}" ;;
esac
