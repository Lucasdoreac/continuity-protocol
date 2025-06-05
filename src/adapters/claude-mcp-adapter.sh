#!/bin/bash
# Claude MCP Adapter - Integração do sistema CONTINUITY com Claude Desktop
# Este script configura a integração do servidor MCP com o Claude Desktop

set -euo pipefail

# Configurações
CONTINUITY_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY"
MCP_TOOL_DIR="$CONTINUITY_DIR/mcp-continuity-tool"
PORT=3457
LOG_FILE="$CONTINUITY_DIR/logs/claude-mcp-adapter.log"
PID_FILE="$CONTINUITY_DIR/claude-mcp-adapter.pid"
CLAUDE_CONFIG_FILE="$HOME/.config/claude/claude_desktop_config.json"
CLAUDE_CONFIG_DIR="$(dirname "$CLAUDE_CONFIG_FILE")"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para logging
log() {
    mkdir -p "$(dirname "$LOG_FILE")"
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

# Verificar dependências
check_dependencies() {
    log "Verificando dependências..."
    
    # Verificar Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js não encontrado. Por favor, instale o Node.js."
        exit 1
    fi
    
    # Verificar jq (necessário para manipular JSON)
    if ! command -v jq &> /dev/null; then
        log_error "jq não encontrado. Por favor, instale o jq para manipular arquivos JSON."
        exit 1
    fi
    
    # Verificar se o diretório MCP Tool existe
    if [[ ! -d "$MCP_TOOL_DIR" ]]; then
        log_error "Diretório MCP Tool não encontrado: $MCP_TOOL_DIR"
        exit 1
    fi
    
    # Verificar se o arquivo index.js existe
    if [[ ! -f "$MCP_TOOL_DIR/index.js" ]]; then
        log_error "Arquivo index.js não encontrado em $MCP_TOOL_DIR"
        exit 1
    fi
    
    log_success "Todas as dependências verificadas."
}

# Iniciar o servidor MCP
start_mcp_server() {
    log "Iniciando servidor MCP na porta $PORT..."
    
    # Verificar se o servidor já está em execução
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null; then
            log_warning "Servidor MCP já está em execução com PID $pid"
            return 0
        else
            log_warning "Arquivo PID encontrado, mas processo não está em execução. Removendo arquivo PID."
            rm -f "$PID_FILE"
        fi
    fi
    
    # Iniciar o servidor em segundo plano
    cd "$MCP_TOOL_DIR"
    PORT=$PORT node index.js > "$LOG_FILE" 2>&1 &
    local pid=$!
    echo $pid > "$PID_FILE"
    
    # Verificar se o servidor iniciou corretamente
    sleep 2
    if ps -p "$pid" > /dev/null; then
        log_success "Servidor MCP iniciado com PID $pid na porta $PORT"
    else
        log_error "Falha ao iniciar o servidor MCP"
        exit 1
    fi
}

# Configurar integração com Claude Desktop
configure_claude_integration() {
    log "Configurando integração com Claude Desktop..."
    
    # Criar diretório de configuração do Claude se não existir
    mkdir -p "$CLAUDE_CONFIG_DIR"
    
    # Verificar se o arquivo de configuração do Claude existe
    if [[ ! -f "$CLAUDE_CONFIG_FILE" ]]; then
        # Criar arquivo de configuração básico se não existir
        log "Criando arquivo de configuração do Claude..."
        echo '{
  "theme": "system",
  "mcpServers": []
}' > "$CLAUDE_CONFIG_FILE"
    fi
    
    # Verificar se o arquivo é um JSON válido
    if ! jq empty "$CLAUDE_CONFIG_FILE" 2>/dev/null; then
        log_error "Arquivo de configuração do Claude não é um JSON válido: $CLAUDE_CONFIG_FILE"
        exit 1
    fi
    
    # Verificar se o servidor MCP já está configurado
    local server_exists=$(jq '.mcpServers[] | select(.url == "http://localhost:'$PORT'") | .name' "$CLAUDE_CONFIG_FILE" 2>/dev/null)
    
    if [[ -n "$server_exists" ]]; then
        log_warning "Servidor MCP já configurado no Claude Desktop: $server_exists"
    else
        # Adicionar servidor MCP à configuração do Claude
        log "Adicionando servidor MCP à configuração do Claude..."
        
        # Criar backup do arquivo de configuração
        cp "$CLAUDE_CONFIG_FILE" "${CLAUDE_CONFIG_FILE}.bak"
        
        # Adicionar servidor MCP
        jq '.mcpServers += [{
            "name": "CONTINUITY",
            "url": "http://localhost:'$PORT'",
            "description": "MCP Continuity Tool para integração com Claude Desktop",
            "enabled": true
        }]' "$CLAUDE_CONFIG_FILE" > "${CLAUDE_CONFIG_FILE}.tmp"
        
        # Verificar se o JSON resultante é válido
        if jq empty "${CLAUDE_CONFIG_FILE}.tmp" 2>/dev/null; then
            mv "${CLAUDE_CONFIG_FILE}.tmp" "$CLAUDE_CONFIG_FILE"
            log_success "Servidor MCP adicionado à configuração do Claude Desktop"
        else
            log_error "Falha ao adicionar servidor MCP à configuração do Claude Desktop"
            rm -f "${CLAUDE_CONFIG_FILE}.tmp"
            exit 1
        fi
    fi
}

# Remover integração com Claude Desktop
remove_claude_integration() {
    log "Removendo integração com Claude Desktop..."
    
    # Verificar se o arquivo de configuração do Claude existe
    if [[ ! -f "$CLAUDE_CONFIG_FILE" ]]; then
        log_warning "Arquivo de configuração do Claude não encontrado: $CLAUDE_CONFIG_FILE"
        return 0
    fi
    
    # Verificar se o arquivo é um JSON válido
    if ! jq empty "$CLAUDE_CONFIG_FILE" 2>/dev/null; then
        log_error "Arquivo de configuração do Claude não é um JSON válido: $CLAUDE_CONFIG_FILE"
        exit 1
    fi
    
    # Criar backup do arquivo de configuração
    cp "$CLAUDE_CONFIG_FILE" "${CLAUDE_CONFIG_FILE}.bak"
    
    # Remover servidor MCP da configuração
    jq '.mcpServers = [.mcpServers[] | select(.url != "http://localhost:'$PORT'")]' "$CLAUDE_CONFIG_FILE" > "${CLAUDE_CONFIG_FILE}.tmp"
    
    # Verificar se o JSON resultante é válido
    if jq empty "${CLAUDE_CONFIG_FILE}.tmp" 2>/dev/null; then
        mv "${CLAUDE_CONFIG_FILE}.tmp" "$CLAUDE_CONFIG_FILE"
        log_success "Servidor MCP removido da configuração do Claude Desktop"
    else
        log_error "Falha ao remover servidor MCP da configuração do Claude Desktop"
        rm -f "${CLAUDE_CONFIG_FILE}.tmp"
        exit 1
    fi
}

# Parar o servidor MCP
stop_mcp_server() {
    log "Parando servidor MCP..."
    
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null; then
            kill "$pid"
            log_success "Servidor MCP com PID $pid encerrado."
        else
            log_warning "Processo com PID $pid não encontrado."
        fi
        rm -f "$PID_FILE"
    else
        log_warning "Arquivo PID não encontrado. O servidor pode não estar em execução."
    fi
}

# Função para exibir status
show_status() {
    echo -e "${BLUE}=== Claude MCP Adapter Status ===${NC}"
    
    # Verificar se o servidor está em execução
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null; then
            echo -e "${GREEN}● Servidor MCP em execução${NC} (PID: $pid, Porta: $PORT)"
        else
            echo -e "${RED}● Servidor MCP não está em execução${NC} (PID inválido: $pid)"
        fi
    else
        echo -e "${RED}● Servidor MCP não está em execução${NC}"
    fi
    
    # Verificar integração Claude
    if [[ -f "$CLAUDE_CONFIG_FILE" ]]; then
        local server_exists=$(jq '.mcpServers[] | select(.url == "http://localhost:'$PORT'") | .name' "$CLAUDE_CONFIG_FILE" 2>/dev/null)
        if [[ -n "$server_exists" ]]; then
            echo -e "${GREEN}● Integração Claude configurada${NC} (Nome: $server_exists)"
        else
            echo -e "${RED}● Integração Claude não configurada${NC}"
        fi
    else
        echo -e "${RED}● Arquivo de configuração do Claude não encontrado${NC}"
    fi
    
    # Status do monitor
    echo -e "${BLUE}--- Status do Monitor ---${NC}"
    "$CONTINUITY_DIR/mcp-self-monitor.sh" status
    
    # Últimas linhas do log
    echo -e "${BLUE}--- Últimas linhas do log ---${NC}"
    tail -n 5 "$LOG_FILE" 2>/dev/null || echo "Arquivo de log não encontrado."
}

# Função para testar a integração
test_integration() {
    log "Testando integração MCP-Claude..."
    
    # Verificar se o servidor está em execução
    if [[ ! -f "$PID_FILE" ]]; then
        log_error "Servidor MCP não está em execução. Inicie-o primeiro com 'start'."
        exit 1
    fi
    
    # Testar conexão com o servidor
    local response=$(curl -s "http://localhost:$PORT/" || echo '{"error": "Falha na conexão"}')
    log "Resposta do servidor: $response"
    
    # Verificar se o servidor está configurado no Claude
    if [[ -f "$CLAUDE_CONFIG_FILE" ]]; then
        local server_exists=$(jq '.mcpServers[] | select(.url == "http://localhost:'$PORT'") | .name' "$CLAUDE_CONFIG_FILE" 2>/dev/null)
        if [[ -n "$server_exists" ]]; then
            log_success "Servidor MCP configurado no Claude Desktop: $server_exists"
        else
            log_error "Servidor MCP não está configurado no Claude Desktop"
        fi
    else
        log_error "Arquivo de configuração do Claude não encontrado: $CLAUDE_CONFIG_FILE"
    fi
    
    # Criar um projeto de teste
    local test_project="claude-mcp-test-$(date +%s)"
    local test_data='{
        "repositoryUrl": "anthropic/claude-mcp-integration",
        "workingDirectory": "/tmp/claude-mcp-test"
    }'
    
    # Enviar requisição para inicializar o projeto
    local init_response=$(curl -s -X POST -H "Content-Type: application/json" -d "$test_data" "http://localhost:$PORT/initialize")
    log "Resposta de inicialização: $init_response"
    
    # Verificar se a inicialização foi bem-sucedida
    if echo "$init_response" | grep -q "projectState"; then
        log_success "Integração MCP-Claude testada com sucesso!"
    else
        log_error "Falha no teste de integração MCP-Claude."
    fi
}

# Função principal
main() {
    local command="$1"
    
    case "$command" in
        "install")
            check_dependencies
            start_mcp_server
            configure_claude_integration
            log_success "Claude MCP Adapter instalado e configurado com sucesso!"
            echo -e "${GREEN}O servidor MCP agora está disponível no Claude Desktop como 'CONTINUITY'${NC}"
            ;;
            
        "uninstall")
            remove_claude_integration
            stop_mcp_server
            log_success "Claude MCP Adapter desinstalado com sucesso!"
            ;;
            
        "start")
            check_dependencies
            start_mcp_server
            log_success "Servidor MCP iniciado com sucesso!"
            ;;
            
        "stop")
            stop_mcp_server
            log_success "Servidor MCP parado com sucesso!"
            ;;
            
        "restart")
            stop_mcp_server
            sleep 2
            check_dependencies
            start_mcp_server
            log_success "Servidor MCP reiniciado com sucesso!"
            ;;
            
        "status")
            show_status
            ;;
            
        "test")
            test_integration
            ;;
            
        *)
            echo "Uso: $0 {install|uninstall|start|stop|restart|status|test}"
            echo ""
            echo "Comandos:"
            echo "  install  - Instala e configura o MCP Adapter no Claude Desktop"
            echo "  uninstall - Remove a integração do Claude Desktop"
            echo "  start    - Inicia apenas o servidor MCP"
            echo "  stop     - Para o servidor MCP"
            echo "  restart  - Reinicia o servidor MCP"
            echo "  status   - Exibe o status atual do servidor e integração"
            echo "  test     - Testa a integração MCP-Claude"
            exit 1
            ;;
    esac
}

# Verificar parâmetros e executar
if [[ $# -lt 1 ]]; then
    echo "Uso: $0 {install|uninstall|start|stop|restart|status|test}"
    exit 1
fi

main "$@"
