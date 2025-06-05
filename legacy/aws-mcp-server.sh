#!/bin/bash
# AWS MCP Server - Integração do sistema CONTINUITY com Amazon CLI como servidor MCP
# Este script inicia o servidor MCP e configura a integração com o Amazon CLI

set -euo pipefail

# Configurações
CONTINUITY_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY"
MCP_TOOL_DIR="$CONTINUITY_DIR/mcp-continuity-tool"
PORT=3456
LOG_FILE="$CONTINUITY_DIR/logs/aws-mcp-server.log"
PID_FILE="$CONTINUITY_DIR/aws-mcp-server.pid"

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
    
    # Verificar AWS CLI
    if ! command -v aws &> /dev/null; then
        log_warning "AWS CLI não encontrado. Algumas funcionalidades podem não estar disponíveis."
    else
        log_success "AWS CLI encontrado: $(aws --version)"
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
    }
    
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

# Configurar integração com AWS CLI
configure_aws_integration() {
    log "Configurando integração com AWS CLI..."
    
    # Verificar se o AWS CLI está configurado
    if ! aws sts get-caller-identity &> /dev/null; then
        log_warning "AWS CLI não configurado ou credenciais inválidas."
        log "Execute 'aws configure' para configurar suas credenciais AWS."
    else
        log_success "AWS CLI configurado corretamente."
        
        # Obter informações da conta AWS
        local account_info=$(aws sts get-caller-identity --output json)
        log "Conta AWS: $account_info"
    fi
    
    # Criar arquivo de configuração MCP para AWS CLI
    local mcp_config_dir="$HOME/.aws/mcp"
    mkdir -p "$mcp_config_dir"
    
    cat > "$mcp_config_dir/continuity.json" << EOF
{
    "name": "continuity",
    "version": "1.0.0",
    "description": "MCP Continuity Tool para integração com AWS CLI",
    "endpoint": "http://localhost:$PORT",
    "tools": [
        {
            "name": "project-state",
            "description": "Gerencia o estado do projeto",
            "path": "/state"
        },
        {
            "name": "continuity-prompt",
            "description": "Gera prompts de continuidade para o projeto",
            "path": "/continuity-prompt"
        },
        {
            "name": "initialize-project",
            "description": "Inicializa um novo projeto ou configura um existente",
            "path": "/initialize"
        }
    ]
}
EOF
    
    log_success "Configuração MCP para AWS CLI criada em $mcp_config_dir/continuity.json"
}

# Monitorar o servidor MCP
monitor_mcp_server() {
    log "Iniciando monitoramento do servidor MCP..."
    
    # Iniciar o script de monitoramento
    "$CONTINUITY_DIR/mcp-self-monitor.sh" start
    
    # Verificar status do servidor a cada 30 segundos
    while true; do
        sleep 30
        
        # Verificar se o processo ainda está em execução
        if [[ -f "$PID_FILE" ]]; then
            local pid=$(cat "$PID_FILE")
            if ! ps -p "$pid" > /dev/null; then
                log_error "Servidor MCP não está mais em execução. Tentando reiniciar..."
                start_mcp_server
            fi
        else
            log_error "Arquivo PID não encontrado. Tentando reiniciar o servidor..."
            start_mcp_server
        fi
        
        # Verificar status do monitor
        "$CONTINUITY_DIR/mcp-self-monitor.sh" status
    done
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
    echo -e "${BLUE}=== AWS MCP Server Status ===${NC}"
    
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
    
    # Verificar integração AWS
    if [[ -f "$HOME/.aws/mcp/continuity.json" ]]; then
        echo -e "${GREEN}● Integração AWS configurada${NC}"
    else
        echo -e "${RED}● Integração AWS não configurada${NC}"
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
    log "Testando integração MCP-AWS..."
    
    # Verificar se o servidor está em execução
    if [[ ! -f "$PID_FILE" ]]; then
        log_error "Servidor MCP não está em execução. Inicie-o primeiro com 'start'."
        exit 1
    fi
    
    # Testar conexão com o servidor
    local response=$(curl -s "http://localhost:$PORT/" || echo '{"error": "Falha na conexão"}')
    log "Resposta do servidor: $response"
    
    # Testar integração com AWS CLI (se disponível)
    if command -v aws &> /dev/null; then
        log "Testando integração com AWS CLI..."
        
        # Criar um projeto de teste
        local test_project="aws-mcp-test-$(date +%s)"
        local test_data='{
            "repositoryUrl": "aws-samples/aws-mcp-integration",
            "workingDirectory": "/tmp/aws-mcp-test"
        }'
        
        # Enviar requisição para inicializar o projeto
        local init_response=$(curl -s -X POST -H "Content-Type: application/json" -d "$test_data" "http://localhost:$PORT/initialize")
        log "Resposta de inicialização: $init_response"
        
        # Verificar se a inicialização foi bem-sucedida
        if echo "$init_response" | grep -q "projectState"; then
            log_success "Integração MCP-AWS testada com sucesso!"
        else
            log_error "Falha no teste de integração MCP-AWS."
        fi
    else
        log_warning "AWS CLI não encontrado. Teste de integração limitado."
    fi
}

# Função principal
main() {
    local command="$1"
    
    case "$command" in
        "start")
            check_dependencies
            start_mcp_server
            configure_aws_integration
            log_success "AWS MCP Server iniciado e configurado com sucesso!"
            echo -e "${GREEN}Para usar com Amazon Q CLI, execute:${NC}"
            echo "q chat --mcp-server http://localhost:$PORT"
            ;;
            
        "stop")
            stop_mcp_server
            log_success "AWS MCP Server parado com sucesso!"
            ;;
            
        "restart")
            stop_mcp_server
            sleep 2
            check_dependencies
            start_mcp_server
            configure_aws_integration
            log_success "AWS MCP Server reiniciado com sucesso!"
            ;;
            
        "status")
            show_status
            ;;
            
        "monitor")
            monitor_mcp_server
            ;;
            
        "test")
            test_integration
            ;;
            
        *)
            echo "Uso: $0 {start|stop|restart|status|monitor|test}"
            echo ""
            echo "Comandos:"
            echo "  start   - Inicia o servidor MCP e configura integração com AWS CLI"
            echo "  stop    - Para o servidor MCP"
            echo "  restart - Reinicia o servidor MCP"
            echo "  status  - Exibe o status atual do servidor e integração"
            echo "  monitor - Inicia monitoramento contínuo do servidor"
            echo "  test    - Testa a integração MCP-AWS"
            exit 1
            ;;
    esac
}

# Verificar parâmetros e executar
if [[ $# -lt 1 ]]; then
    echo "Uso: $0 {start|stop|restart|status|monitor|test}"
    exit 1
fi

main "$@"
