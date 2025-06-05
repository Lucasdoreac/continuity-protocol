#!/bin/bash
# MCP Continuity Integration
# Integra o sistema de memória compartilhada com AWS CLI e Claude Desktop

set -euo pipefail

# Configurações
CONTINUITY_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY"
MEMORY_MANAGER="$CONTINUITY_DIR/shared-memory-manager.sh"
AWS_MCP_SERVER="$CONTINUITY_DIR/aws-mcp-server.sh"
CLAUDE_MCP_ADAPTER="$CONTINUITY_DIR/claude-mcp-adapter.sh"
LOG_FILE="$CONTINUITY_DIR/logs/mcp-integration.log"

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
    
    # Verificar se os scripts existem
    for script in "$MEMORY_MANAGER" "$AWS_MCP_SERVER" "$CLAUDE_MCP_ADAPTER"; do
        if [[ ! -f "$script" ]]; then
            log_error "Script não encontrado: $script"
            exit 1
        fi
        
        if [[ ! -x "$script" ]]; then
            log_error "Script não executável: $script"
            chmod +x "$script"
            log_warning "Permissão de execução adicionada: $script"
        fi
    done
    
    # Verificar jq
    if ! command -v jq &> /dev/null; then
        log_error "jq não encontrado. Por favor, instale o jq: brew install jq"
        exit 1
    fi
    
    # Verificar Node.js
    if ! command -v node &> /dev/null; then
        log_warning "Node.js não encontrado. Algumas funcionalidades podem não estar disponíveis."
    fi
    
    log_success "Todas as dependências verificadas."
}

# Inicializar sistema de memória compartilhada
init_shared_memory() {
    log "Inicializando sistema de memória compartilhada..."
    "$MEMORY_MANAGER" init
    "$MEMORY_MANAGER" capture
    log_success "Sistema de memória compartilhada inicializado."
}

# Iniciar servidores MCP
start_mcp_servers() {
    log "Iniciando servidores MCP..."
    
    # Iniciar servidor AWS MCP
    "$AWS_MCP_SERVER" start &
    local aws_pid=$!
    
    # Aguardar um pouco para garantir que o primeiro servidor iniciou
    sleep 2
    
    # Iniciar adaptador Claude MCP
    "$CLAUDE_MCP_ADAPTER" start &
    local claude_pid=$!
    
    # Aguardar inicialização
    sleep 3
    
    # Verificar se os processos estão em execução
    if ps -p $aws_pid > /dev/null; then
        log_success "Servidor AWS MCP iniciado com PID $aws_pid"
    else
        log_error "Falha ao iniciar servidor AWS MCP"
    fi
    
    if ps -p $claude_pid > /dev/null; then
        log_success "Adaptador Claude MCP iniciado com PID $claude_pid"
    else
        log_error "Falha ao iniciar adaptador Claude MCP"
    fi
    
    # Salvar PIDs
    echo "$aws_pid $claude_pid" > "$CONTINUITY_DIR/mcp-servers.pid"
    log "PIDs dos servidores salvos em $CONTINUITY_DIR/mcp-servers.pid"
}

# Parar servidores MCP
stop_mcp_servers() {
    log "Parando servidores MCP..."
    
    # Parar servidor AWS MCP
    "$AWS_MCP_SERVER" stop
    
    # Parar adaptador Claude MCP
    "$CLAUDE_MCP_ADAPTER" stop
    
    # Remover arquivo de PIDs
    rm -f "$CONTINUITY_DIR/mcp-servers.pid"
    
    log_success "Servidores MCP parados."
}

# Configurar integração com AWS CLI
configure_aws_integration() {
    log "Configurando integração com AWS CLI..."
    
    # Criar sessão para AWS CLI
    "$MEMORY_MANAGER" create-session "aws-cli" "Sessão para Amazon Q CLI"
    
    # Definir foco inicial
    "$MEMORY_MANAGER" focus "aws-cli" "Integração MCP Continuity com Amazon Q CLI"
    
    # Adicionar projetos relevantes
    "$MEMORY_MANAGER" add-project "aws-cli" "mcp-continuity-tool" "$CONTINUITY_DIR/mcp-continuity-tool"
    "$MEMORY_MANAGER" add-project "aws-cli" "CONTINUITY" "$CONTINUITY_DIR"
    
    log_success "Integração com AWS CLI configurada."
}

# Configurar integração com Claude Desktop
configure_claude_integration() {
    log "Configurando integração com Claude Desktop..."
    
    # Criar sessão para Claude Desktop
    "$MEMORY_MANAGER" create-session "claude-desktop" "Sessão para Claude Desktop"
    
    # Definir foco inicial
    "$MEMORY_MANAGER" focus "claude-desktop" "Integração MCP Continuity com Claude Desktop"
    
    # Adicionar projetos relevantes
    "$MEMORY_MANAGER" add-project "claude-desktop" "mcp-continuity-tool" "$CONTINUITY_DIR/mcp-continuity-tool"
    "$MEMORY_MANAGER" add-project "claude-desktop" "CONTINUITY" "$CONTINUITY_DIR"
    
    log_success "Integração com Claude Desktop configurada."
}

# Configurar hooks para interceptar perguntas de continuidade
configure_continuity_hooks() {
    log "Configurando hooks para perguntas de continuidade..."
    
    # Criar diretório para hooks
    mkdir -p "$CONTINUITY_DIR/hooks"
    
    # Criar hook para AWS CLI
    cat > "$CONTINUITY_DIR/hooks/aws-cli-hook.sh" << 'EOF'
#!/bin/bash
# Hook para interceptar perguntas de continuidade no AWS CLI

CONTINUITY_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY"
MEMORY_MANAGER="$CONTINUITY_DIR/shared-memory-manager.sh"

# Verificar se a entrada é uma pergunta de continuidade
if "$MEMORY_MANAGER" check-question "$*" &>/dev/null; then
    # Registrar a pergunta
    "$MEMORY_MANAGER" register-question "aws-cli" "$*"
    
    # Gerar resposta de continuidade
    "$MEMORY_MANAGER" continuity-response "aws-cli"
    exit 0
fi

# Se não for uma pergunta de continuidade, continuar normalmente
exit 1
EOF
    
    # Criar hook para Claude Desktop
    cat > "$CONTINUITY_DIR/hooks/claude-desktop-hook.sh" << 'EOF'
#!/bin/bash
# Hook para interceptar perguntas de continuidade no Claude Desktop

CONTINUITY_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY"
MEMORY_MANAGER="$CONTINUITY_DIR/shared-memory-manager.sh"

# Verificar se a entrada é uma pergunta de continuidade
if "$MEMORY_MANAGER" check-question "$*" &>/dev/null; then
    # Registrar a pergunta
    "$MEMORY_MANAGER" register-question "claude-desktop" "$*"
    
    # Gerar resposta de continuidade
    "$MEMORY_MANAGER" continuity-response "claude-desktop"
    exit 0
fi

# Se não for uma pergunta de continuidade, continuar normalmente
exit 1
EOF
    
    # Tornar hooks executáveis
    chmod +x "$CONTINUITY_DIR/hooks/aws-cli-hook.sh"
    chmod +x "$CONTINUITY_DIR/hooks/claude-desktop-hook.sh"
    
    log_success "Hooks para perguntas de continuidade configurados."
}

# Criar arquivo de configuração MCP para AWS CLI
create_aws_mcp_config() {
    log "Criando configuração MCP para AWS CLI..."
    
    # Criar diretório de configuração
    mkdir -p "$HOME/.aws/mcp"
    
    # Criar arquivo de configuração
    cat > "$HOME/.aws/mcp/continuity.json" << EOF
{
    "name": "continuity",
    "version": "1.0.0",
    "description": "MCP Continuity Tool com memória compartilhada",
    "endpoint": "http://localhost:3456",
    "tools": [
        {
            "name": "continuity-check",
            "description": "Verifica se uma pergunta é sobre continuidade",
            "path": "/continuity-check",
            "hook": "$CONTINUITY_DIR/hooks/aws-cli-hook.sh"
        },
        {
            "name": "continuity-response",
            "description": "Gera resposta de continuidade",
            "path": "/continuity-response"
        },
        {
            "name": "session-context",
            "description": "Gerencia contexto de sessão",
            "path": "/session-context"
        }
    ]
}
EOF
    
    log_success "Configuração MCP para AWS CLI criada em $HOME/.aws/mcp/continuity.json"
}

# Criar arquivo de configuração MCP para Claude Desktop
create_claude_mcp_config() {
    log "Criando configuração MCP para Claude Desktop..."
    
    # Criar diretório de configuração
    mkdir -p "$HOME/.config/claude"
    
    # Verificar se o arquivo de configuração já existe
    local config_file="$HOME/.config/claude/claude_desktop_config.json"
    if [[ -f "$config_file" ]]; then
        # Fazer backup do arquivo existente
        cp "$config_file" "${config_file}.bak"
        log "Backup do arquivo de configuração criado: ${config_file}.bak"
        
        # Atualizar configuração existente
        jq '.mcpServers += [{
            "name": "CONTINUITY",
            "url": "http://localhost:3457",
            "description": "MCP Continuity Tool com memória compartilhada",
            "enabled": true,
            "hooks": {
                "input": "'$CONTINUITY_DIR'/hooks/claude-desktop-hook.sh"
            }
        }]' "$config_file" > "${config_file}.tmp"
        
        # Verificar se o JSON resultante é válido
        if jq empty "${config_file}.tmp" 2>/dev/null; then
            mv "${config_file}.tmp" "$config_file"
            log_success "Configuração MCP para Claude Desktop atualizada"
        else
            log_error "Falha ao atualizar configuração do Claude Desktop"
            rm -f "${config_file}.tmp"
            exit 1
        fi
    else
        # Criar novo arquivo de configuração
        cat > "$config_file" << EOF
{
  "theme": "system",
  "mcpServers": [
    {
      "name": "CONTINUITY",
      "url": "http://localhost:3457",
      "description": "MCP Continuity Tool com memória compartilhada",
      "enabled": true,
      "hooks": {
        "input": "$CONTINUITY_DIR/hooks/claude-desktop-hook.sh"
      }
    }
  ]
}
EOF
        log_success "Configuração MCP para Claude Desktop criada em $config_file"
    fi
}

# Adicionar repositórios ao contexto
add_repositories() {
    log "Adicionando repositórios ao contexto..."
    
    # Adicionar repositórios ao contexto AWS CLI
    "$MEMORY_MANAGER" add-project "aws-cli" "mcp-continuity-tool" "https://github.com/Lucasdoreac/mcp-continuity-tool/"
    
    # Adicionar repositórios ao contexto Claude Desktop
    "$MEMORY_MANAGER" add-project "claude-desktop" "mcp-continuity-tool" "https://github.com/Lucasdoreac/mcp-continuity-tool/"
    
    log_success "Repositórios adicionados ao contexto."
}

# Exibir status da integração
show_status() {
    echo -e "${BLUE}=== MCP Continuity Integration Status ===${NC}"
    
    # Verificar status dos servidores MCP
    echo -e "${BLUE}--- Servidores MCP ---${NC}"
    "$AWS_MCP_SERVER" status
    echo ""
    "$CLAUDE_MCP_ADAPTER" status
    
    # Verificar sessões disponíveis
    echo -e "${BLUE}--- Sessões Disponíveis ---${NC}"
    "$MEMORY_MANAGER" list-sessions
    
    # Verificar contexto atual
    echo -e "${BLUE}--- Contexto Atual ---${NC}"
    "$MEMORY_MANAGER" current-context | head -20
    
    # Verificar configurações MCP
    echo -e "${BLUE}--- Configurações MCP ---${NC}"
    if [[ -f "$HOME/.aws/mcp/continuity.json" ]]; then
        echo -e "${GREEN}● Configuração AWS CLI encontrada${NC}"
    else
        echo -e "${RED}● Configuração AWS CLI não encontrada${NC}"
    fi
    
    if [[ -f "$HOME/.config/claude/claude_desktop_config.json" ]]; then
        echo -e "${GREEN}● Configuração Claude Desktop encontrada${NC}"
    else
        echo -e "${RED}● Configuração Claude Desktop não encontrada${NC}"
    fi
}

# Testar integração
test_integration() {
    log "Testando integração..."
    
    # Testar pergunta de continuidade
    echo -e "${BLUE}Testando pergunta de continuidade:${NC} onde paramos?"
    if "$MEMORY_MANAGER" check-question "onde paramos?" &>/dev/null; then
        echo -e "${GREEN}✓ Pergunta de continuidade detectada corretamente${NC}"
    else
        echo -e "${RED}✗ Falha ao detectar pergunta de continuidade${NC}"
    fi
    
    # Testar geração de resposta
    echo -e "${BLUE}Testando geração de resposta de continuidade:${NC}"
    "$MEMORY_MANAGER" continuity-response "aws-cli"
    
    # Testar servidores MCP
    echo -e "${BLUE}Testando servidores MCP:${NC}"
    "$AWS_MCP_SERVER" test
    "$CLAUDE_MCP_ADAPTER" test
    
    log_success "Testes de integração concluídos."
}

# Função principal
main() {
    local command="$1"
    
    case "$command" in
        "install")
            check_dependencies
            init_shared_memory
            configure_continuity_hooks
            create_aws_mcp_config
            create_claude_mcp_config
            configure_aws_integration
            configure_claude_integration
            add_repositories
            log_success "MCP Continuity Integration instalado com sucesso!"
            ;;
            
        "start")
            check_dependencies
            start_mcp_servers
            log_success "Servidores MCP iniciados com sucesso!"
            ;;
            
        "stop")
            stop_mcp_servers
            log_success "Servidores MCP parados com sucesso!"
            ;;
            
        "restart")
            stop_mcp_servers
            sleep 2
            start_mcp_servers
            log_success "Servidores MCP reiniciados com sucesso!"
            ;;
            
        "status")
            show_status
            ;;
            
        "test")
            test_integration
            ;;
            
        *)
            echo "Uso: $0 {install|start|stop|restart|status|test}"
            echo ""
            echo "Comandos:"
            echo "  install  - Instalar e configurar integração MCP Continuity"
            echo "  start    - Iniciar servidores MCP"
            echo "  stop     - Parar servidores MCP"
            echo "  restart  - Reiniciar servidores MCP"
            echo "  status   - Exibir status da integração"
            echo "  test     - Testar integração"
            exit 1
            ;;
    esac
}

# Verificar parâmetros e executar
if [[ $# -lt 1 ]]; then
    echo "Uso: $0 {install|start|stop|restart|status|test}"
    exit 1
fi

main "$@"
