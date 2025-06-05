#!/bin/bash
# Script para iniciar o servidor MCP unificado do Continuity Protocol
# Este script inicia todos os componentes necessários para o funcionamento do sistema

# Diretório base do Continuity Protocol
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGS_DIR="$BASE_DIR/logs"
CORE_DIR="$BASE_DIR/core/mcp"

# Criar diretório de logs se não existir
mkdir -p "$LOGS_DIR"

# Função para verificar se um processo está rodando
is_process_running() {
    local pid=$1
    if ps -p "$pid" > /dev/null; then
        return 0  # Processo está rodando
    else
        return 1  # Processo não está rodando
    fi
}

# Função para iniciar um servidor MCP
start_mcp_server() {
    local server_type=$1
    local agent_type=$2
    local log_file="$LOGS_DIR/${server_type}_${agent_type}.log"
    
    echo "Iniciando servidor MCP para $agent_type..."
    python "$CORE_DIR/mcp_server_extension.py" "$server_type" "$agent_type" stdio > "$log_file" 2>&1 &
    local pid=$!
    
    # Verificar se o processo iniciou corretamente
    sleep 1
    if is_process_running $pid; then
        echo "✅ Servidor MCP para $agent_type iniciado com PID $pid"
        echo $pid > "$LOGS_DIR/${server_type}_${agent_type}.pid"
    else
        echo "❌ Falha ao iniciar servidor MCP para $agent_type"
        return 1
    fi
}

# Função para iniciar o servidor principal
start_main_server() {
    local log_file="$LOGS_DIR/main_server.log"
    
    echo "Iniciando servidor principal..."
    python "$BASE_DIR/mcp-server.py" > "$log_file" 2>&1 &
    local pid=$!
    
    # Verificar se o processo iniciou corretamente
    sleep 1
    if is_process_running $pid; then
        echo "✅ Servidor principal iniciado com PID $pid"
        echo $pid > "$LOGS_DIR/main_server.pid"
    else
        echo "❌ Falha ao iniciar servidor principal"
        return 1
    fi
}

# Função para parar todos os servidores
stop_all_servers() {
    echo "Parando todos os servidores..."
    
    # Parar servidores MCP
    for pid_file in "$LOGS_DIR"/*.pid; do
        if [ -f "$pid_file" ]; then
            pid=$(cat "$pid_file")
            if is_process_running $pid; then
                echo "Parando processo $pid..."
                kill $pid
                rm "$pid_file"
            fi
        fi
    done
    
    echo "✅ Todos os servidores parados"
}

# Função para verificar status dos servidores
check_status() {
    echo "Status dos servidores:"
    
    # Verificar servidores MCP
    for pid_file in "$LOGS_DIR"/*.pid; do
        if [ -f "$pid_file" ]; then
            server_name=$(basename "$pid_file" .pid)
            pid=$(cat "$pid_file")
            if is_process_running $pid; then
                echo "✅ $server_name: RODANDO (PID $pid)"
            else
                echo "❌ $server_name: PARADO (PID $pid não encontrado)"
                rm "$pid_file"
            fi
        fi
    done
    
    # Verificar se não há servidores rodando
    if [ ! "$(ls -A "$LOGS_DIR"/*.pid 2>/dev/null)" ]; then
        echo "❌ Nenhum servidor rodando"
    fi
}

# Processar argumentos
case "$1" in
    start)
        echo "=== Iniciando Continuity Protocol ==="
        # Iniciar servidor principal
        start_main_server
        
        # Iniciar servidores MCP para diferentes agentes
        start_mcp_server "continuity-protocol" "amazon_q_cli"
        start_mcp_server "continuity-protocol-claude" "claude_desktop"
        
        echo "=== Continuity Protocol iniciado ==="
        ;;
    stop)
        echo "=== Parando Continuity Protocol ==="
        stop_all_servers
        echo "=== Continuity Protocol parado ==="
        ;;
    restart)
        echo "=== Reiniciando Continuity Protocol ==="
        stop_all_servers
        sleep 2
        start_main_server
        start_mcp_server "continuity-protocol" "amazon_q_cli"
        start_mcp_server "continuity-protocol-claude" "claude_desktop"
        echo "=== Continuity Protocol reiniciado ==="
        ;;
    status)
        check_status
        ;;
    *)
        echo "Uso: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac

exit 0
