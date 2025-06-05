#!/bin/bash
# Script para iniciar o servidor MCP aprimorado do Continuity Protocol
# Este script inicia o servidor MCP aprimorado com recursos da Etapa 2

# Diretório base do Continuity Protocol
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGS_DIR="$BASE_DIR/logs"

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

# Função para iniciar o servidor MCP aprimorado
start_enhanced_mcp_server() {
    local server_name=$1
    local transport=$2
    local log_file="$LOGS_DIR/enhanced_mcp_server.log"
    
    echo "Iniciando servidor MCP aprimorado..."
    python3 "$BASE_DIR/enhanced_mcp_server.py" "$server_name" "$transport" > "$log_file" 2>&1 &
    local pid=$!
    
    # Verificar se o processo iniciou corretamente
    sleep 1
    if is_process_running $pid; then
        echo "✅ Servidor MCP aprimorado iniciado com PID $pid"
        echo $pid > "$LOGS_DIR/enhanced_mcp_server.pid"
    else
        echo "❌ Falha ao iniciar servidor MCP aprimorado"
        return 1
    fi
}

# Função para parar o servidor
stop_server() {
    echo "Parando servidor MCP aprimorado..."
    
    # Parar servidor MCP aprimorado
    local pid_file="$LOGS_DIR/enhanced_mcp_server.pid"
    if [ -f "$pid_file" ]; then
        pid=$(cat "$pid_file")
        if is_process_running $pid; then
            echo "Parando processo $pid..."
            kill $pid
            rm "$pid_file"
        fi
    fi
    
    echo "✅ Servidor MCP aprimorado parado"
}

# Função para verificar status do servidor
check_status() {
    echo "Status do servidor MCP aprimorado:"
    
    # Verificar servidor MCP aprimorado
    local pid_file="$LOGS_DIR/enhanced_mcp_server.pid"
    if [ -f "$pid_file" ]; then
        pid=$(cat "$pid_file")
        if is_process_running $pid; then
            echo "✅ Servidor MCP aprimorado: RODANDO (PID $pid)"
        else
            echo "❌ Servidor MCP aprimorado: PARADO (PID $pid não encontrado)"
            rm "$pid_file"
        fi
    else
        echo "❌ Servidor MCP aprimorado: PARADO (PID não encontrado)"
    fi
}

# Processar argumentos
case "$1" in
    start)
        echo "=== Iniciando Servidor MCP Aprimorado ==="
        # Iniciar servidor MCP aprimorado
        start_enhanced_mcp_server "enhanced-continuity-protocol" "stdio"
        echo "=== Servidor MCP Aprimorado iniciado ==="
        ;;
    stop)
        echo "=== Parando Servidor MCP Aprimorado ==="
        stop_server
        echo "=== Servidor MCP Aprimorado parado ==="
        ;;
    restart)
        echo "=== Reiniciando Servidor MCP Aprimorado ==="
        stop_server
        sleep 2
        start_enhanced_mcp_server "enhanced-continuity-protocol" "stdio"
        echo "=== Servidor MCP Aprimorado reiniciado ==="
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
