#!/bin/bash
# Shared Memory Manager para MCP CONTINUITY
# Gerencia memória compartilhada entre AWS CLI e Claude Desktop

set -euo pipefail

# Configurações
CONTINUITY_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY"
MEMORY_DIR="$CONTINUITY_DIR/shared-memory"
SESSIONS_DIR="$MEMORY_DIR/sessions"
CONTEXT_FILE="$MEMORY_DIR/current-context.json"
LOG_FILE="$MEMORY_DIR/memory-manager.log"

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

# Inicializar diretórios
init_directories() {
    mkdir -p "$MEMORY_DIR"
    mkdir -p "$SESSIONS_DIR"
    
    # Criar arquivo de contexto inicial se não existir
    if [[ ! -f "$CONTEXT_FILE" ]]; then
        echo '{
  "current_session": "",
  "last_updated": "",
  "active_projects": [],
  "current_focus": "",
  "open_files": [],
  "active_applications": [],
  "last_command": "",
  "last_question": "",
  "last_response": ""
}' > "$CONTEXT_FILE"
    fi
    
    log_success "Diretórios e arquivos inicializados"
}

# Capturar contexto do sistema
capture_system_context() {
    log "Capturando contexto do sistema..."
    
    # Capturar diretório atual
    local current_dir=$(pwd)
    
    # Capturar aplicações em execução (top 5)
    local running_apps=$(ps aux | grep -v grep | head -5 | awk '{print $11}' | xargs -I{} basename {} 2>/dev/null || echo "")
    
    # Capturar arquivos recentemente modificados no diretório atual
    local recent_files=$(find . -type f -not -path "*/\.*" -mtime -1 | head -5 2>/dev/null || echo "")
    
    # Capturar git branch se estiver em um repositório git
    local git_branch=""
    if command -v git &> /dev/null && git rev-parse --is-inside-work-tree &> /dev/null; then
        git_branch=$(git branch --show-current 2>/dev/null || echo "")
    fi
    
    # Atualizar contexto
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")
    local temp_file=$(mktemp)
    
    jq --arg timestamp "$timestamp" \
       --arg dir "$current_dir" \
       --arg git_branch "$git_branch" \
       '.last_updated = $timestamp | .system_context.current_directory = $dir | .system_context.git_branch = $git_branch' \
       "$CONTEXT_FILE" > "$temp_file"
    
    # Adicionar aplicações em execução
    echo "$running_apps" | jq -R '[inputs]' | \
    jq -s '.[0] * {"system_context": {"running_applications": .[1]}}' "$temp_file" - > "${temp_file}.2"
    
    # Adicionar arquivos recentes
    echo "$recent_files" | jq -R '[inputs]' | \
    jq -s '.[0] * {"system_context": {"recent_files": .[1]}}' "${temp_file}.2" - > "$CONTEXT_FILE"
    
    # Limpar arquivos temporários
    rm -f "$temp_file" "${temp_file}.2"
    
    log_success "Contexto do sistema capturado"
}

# Salvar contexto de sessão
save_session_context() {
    local session_id="$1"
    local context="$2"
    
    # Criar diretório de sessão se não existir
    mkdir -p "$SESSIONS_DIR/$session_id"
    
    # Salvar contexto
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")
    local context_file="$SESSIONS_DIR/$session_id/context.json"
    
    echo "$context" | jq --arg timestamp "$timestamp" '. + {last_updated: $timestamp}' > "$context_file"
    
    # Atualizar contexto atual
    jq --arg session_id "$session_id" '.current_session = $session_id' "$CONTEXT_FILE" > "${CONTEXT_FILE}.tmp"
    mv "${CONTEXT_FILE}.tmp" "$CONTEXT_FILE"
    
    log_success "Contexto da sessão $session_id salvo"
}

# Carregar contexto de sessão
load_session_context() {
    local session_id="$1"
    local context_file="$SESSIONS_DIR/$session_id/context.json"
    
    if [[ -f "$context_file" ]]; then
        cat "$context_file"
        log_success "Contexto da sessão $session_id carregado"
    else
        log_error "Contexto da sessão $session_id não encontrado"
        echo "{}"
        return 1
    fi
}

# Listar sessões disponíveis
list_sessions() {
    log "Listando sessões disponíveis..."
    
    local sessions=$(find "$SESSIONS_DIR" -maxdepth 1 -type d | grep -v "^$SESSIONS_DIR\$" | xargs -I{} basename {} 2>/dev/null || echo "")
    
    if [[ -z "$sessions" ]]; then
        echo "Nenhuma sessão encontrada"
        return 0
    fi
    
    echo "Sessões disponíveis:"
    for session in $sessions; do
        local context_file="$SESSIONS_DIR/$session/context.json"
        if [[ -f "$context_file" ]]; then
            local last_updated=$(jq -r '.last_updated // "N/A"' "$context_file")
            local focus=$(jq -r '.current_focus // "N/A"' "$context_file")
            echo "- $session (Atualizado: $last_updated, Foco: $focus)"
        else
            echo "- $session (Sem contexto)"
        fi
    done
}

# Registrar pergunta "onde paramos?"
register_continuity_question() {
    local session_id="$1"
    local question="$2"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")
    
    # Atualizar contexto atual
    jq --arg question "$question" --arg timestamp "$timestamp" \
       '.last_question = $question | .last_question_time = $timestamp' \
       "$CONTEXT_FILE" > "${CONTEXT_FILE}.tmp"
    mv "${CONTEXT_FILE}.tmp" "$CONTEXT_FILE"
    
    # Atualizar contexto da sessão se existir
    local context_file="$SESSIONS_DIR/$session_id/context.json"
    if [[ -f "$context_file" ]]; then
        jq --arg question "$question" --arg timestamp "$timestamp" \
           '.last_question = $question | .last_question_time = $timestamp' \
           "$context_file" > "${context_file}.tmp"
        mv "${context_file}.tmp" "$context_file"
    fi
    
    log "Pergunta de continuidade registrada: $question"
}

# Registrar resposta à pergunta "onde paramos?"
register_continuity_response() {
    local session_id="$1"
    local response="$2"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")
    
    # Atualizar contexto atual
    jq --arg response "$response" --arg timestamp "$timestamp" \
       '.last_response = $response | .last_response_time = $timestamp' \
       "$CONTEXT_FILE" > "${CONTEXT_FILE}.tmp"
    mv "${CONTEXT_FILE}.tmp" "$CONTEXT_FILE"
    
    # Atualizar contexto da sessão se existir
    local context_file="$SESSIONS_DIR/$session_id/context.json"
    if [[ -f "$context_file" ]]; then
        jq --arg response "$response" --arg timestamp "$timestamp" \
           '.last_response = $response | .last_response_time = $timestamp' \
           "$context_file" > "${context_file}.tmp"
        mv "${context_file}.tmp" "$context_file"
    fi
    
    log "Resposta de continuidade registrada"
}

# Detectar se uma pergunta é sobre continuidade
is_continuity_question() {
    local question="$1"
    local lowercase_question=$(echo "$question" | tr '[:upper:]' '[:lower:]')
    
    if [[ "$lowercase_question" =~ (onde|where|what|o que|em que|qual).*(paramos|estamos|trabalhando|working|left off|continuamos|continue) ]]; then
        return 0  # É uma pergunta de continuidade
    else
        return 1  # Não é uma pergunta de continuidade
    fi
}

# Atualizar foco atual
update_current_focus() {
    local session_id="$1"
    local focus="$2"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")
    
    # Atualizar contexto atual
    jq --arg focus "$focus" --arg timestamp "$timestamp" \
       '.current_focus = $focus | .focus_updated = $timestamp' \
       "$CONTEXT_FILE" > "${CONTEXT_FILE}.tmp"
    mv "${CONTEXT_FILE}.tmp" "$CONTEXT_FILE"
    
    # Atualizar contexto da sessão se existir
    local context_file="$SESSIONS_DIR/$session_id/context.json"
    if [[ -f "$context_file" ]]; then
        jq --arg focus "$focus" --arg timestamp "$timestamp" \
           '.current_focus = $focus | .focus_updated = $timestamp' \
           "$context_file" > "${context_file}.tmp"
        mv "${context_file}.tmp" "$context_file"
    fi
    
    log "Foco atual atualizado: $focus"
}

# Adicionar projeto ativo
add_active_project() {
    local session_id="$1"
    local project_name="$2"
    local project_path="$3"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")
    
    # Criar objeto de projeto
    local project_json=$(jq -n \
                         --arg name "$project_name" \
                         --arg path "$project_path" \
                         --arg timestamp "$timestamp" \
                         '{name: $name, path: $path, added: $timestamp}')
    
    # Atualizar contexto atual
    jq --argjson project "$project_json" \
       '.active_projects += [$project]' \
       "$CONTEXT_FILE" > "${CONTEXT_FILE}.tmp"
    mv "${CONTEXT_FILE}.tmp" "$CONTEXT_FILE"
    
    # Atualizar contexto da sessão se existir
    local context_file="$SESSIONS_DIR/$session_id/context.json"
    if [[ -f "$context_file" ]]; then
        jq --argjson project "$project_json" \
           '.active_projects += [$project]' \
           "$context_file" > "${context_file}.tmp"
        mv "${context_file}.tmp" "$context_file"
    fi
    
    log "Projeto ativo adicionado: $project_name ($project_path)"
}

# Gerar resposta de continuidade
generate_continuity_response() {
    local session_id="$1"
    
    # Carregar contexto atual
    local context=$(cat "$CONTEXT_FILE")
    
    # Carregar contexto da sessão se existir
    local session_context="{}"
    local context_file="$SESSIONS_DIR/$session_id/context.json"
    if [[ -f "$context_file" ]]; then
        session_context=$(cat "$context_file")
    fi
    
    # Extrair informações relevantes
    local current_focus=$(echo "$context" | jq -r '.current_focus // "Nenhum foco definido"')
    local last_updated=$(echo "$context" | jq -r '.last_updated // "N/A"')
    local active_projects=$(echo "$context" | jq -r '.active_projects | length')
    local current_dir=$(echo "$context" | jq -r '.system_context.current_directory // "N/A"')
    local git_branch=$(echo "$context" | jq -r '.system_context.git_branch // "N/A"')
    
    # Gerar resposta
    cat << EOF
📋 Resumo de Continuidade (Sessão: $session_id)
==============================================

🎯 Foco atual: $current_focus
📂 Diretório: $current_dir
🌿 Branch Git: $git_branch
📊 Projetos ativos: $active_projects
🕒 Última atualização: $last_updated

📝 Projetos ativos:
$(echo "$context" | jq -r '.active_projects[] | "- " + .name + " (" + .path + ")"')

🔄 Próximos passos sugeridos:
- Continuar trabalhando no foco atual: $current_focus
- Verificar os arquivos recentes no diretório atual
- Atualizar o status do projeto

Para mais detalhes, use 'shared-memory-manager.sh details $session_id'
EOF
}

# Mostrar detalhes completos da sessão
show_session_details() {
    local session_id="$1"
    local context_file="$SESSIONS_DIR/$session_id/context.json"
    
    if [[ -f "$context_file" ]]; then
        echo -e "${BLUE}=== Detalhes da Sessão: $session_id ===${NC}"
        jq '.' "$context_file"
    else
        log_error "Sessão $session_id não encontrada"
        return 1
    fi
}

# Criar nova sessão
create_session() {
    local session_id="$1"
    local description="$2"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")
    
    # Criar diretório de sessão
    mkdir -p "$SESSIONS_DIR/$session_id"
    
    # Criar contexto inicial
    local context='{
      "session_id": "'$session_id'",
      "description": "'$description'",
      "created": "'$timestamp'",
      "last_updated": "'$timestamp'",
      "current_focus": "",
      "active_projects": [],
      "system_context": {},
      "history": []
    }'
    
    # Salvar contexto
    echo "$context" > "$SESSIONS_DIR/$session_id/context.json"
    
    # Atualizar contexto atual
    jq --arg session_id "$session_id" '.current_session = $session_id' "$CONTEXT_FILE" > "${CONTEXT_FILE}.tmp"
    mv "${CONTEXT_FILE}.tmp" "$CONTEXT_FILE"
    
    log_success "Sessão $session_id criada com sucesso"
}

# Função principal
main() {
    local command="$1"
    shift
    
    # Inicializar diretórios
    init_directories
    
    case "$command" in
        "init")
            log "Inicializando sistema de memória compartilhada..."
            init_directories
            log_success "Sistema de memória compartilhada inicializado"
            ;;
            
        "capture")
            log "Capturando contexto do sistema..."
            capture_system_context
            ;;
            
        "create-session")
            if [[ $# -lt 1 ]]; then
                log_error "Uso: $0 create-session <session_id> [description]"
                exit 1
            fi
            local session_id="$1"
            local description="${2:-Sessão sem descrição}"
            create_session "$session_id" "$description"
            ;;
            
        "list-sessions")
            list_sessions
            ;;
            
        "focus")
            if [[ $# -lt 2 ]]; then
                log_error "Uso: $0 focus <session_id> <focus_description>"
                exit 1
            fi
            local session_id="$1"
            local focus="$2"
            update_current_focus "$session_id" "$focus"
            ;;
            
        "add-project")
            if [[ $# -lt 3 ]]; then
                log_error "Uso: $0 add-project <session_id> <project_name> <project_path>"
                exit 1
            fi
            local session_id="$1"
            local project_name="$2"
            local project_path="$3"
            add_active_project "$session_id" "$project_name" "$project_path"
            ;;
            
        "check-question")
            if [[ $# -lt 1 ]]; then
                log_error "Uso: $0 check-question <question>"
                exit 1
            fi
            local question="$*"
            if is_continuity_question "$question"; then
                echo "É uma pergunta de continuidade"
                exit 0
            else
                echo "Não é uma pergunta de continuidade"
                exit 1
            fi
            ;;
            
        "register-question")
            if [[ $# -lt 2 ]]; then
                log_error "Uso: $0 register-question <session_id> <question>"
                exit 1
            fi
            local session_id="$1"
            local question="${@:2}"
            register_continuity_question "$session_id" "$question"
            ;;
            
        "register-response")
            if [[ $# -lt 2 ]]; then
                log_error "Uso: $0 register-response <session_id> <response_file>"
                exit 1
            fi
            local session_id="$1"
            local response_file="$2"
            if [[ -f "$response_file" ]]; then
                local response=$(cat "$response_file")
                register_continuity_response "$session_id" "$response"
            else
                log_error "Arquivo de resposta não encontrado: $response_file"
                exit 1
            fi
            ;;
            
        "continuity-response")
            if [[ $# -lt 1 ]]; then
                log_error "Uso: $0 continuity-response <session_id>"
                exit 1
            fi
            local session_id="$1"
            generate_continuity_response "$session_id"
            ;;
            
        "details")
            if [[ $# -lt 1 ]]; then
                log_error "Uso: $0 details <session_id>"
                exit 1
            fi
            local session_id="$1"
            show_session_details "$session_id"
            ;;
            
        "current-context")
            echo -e "${BLUE}=== Contexto Atual ===${NC}"
            jq '.' "$CONTEXT_FILE"
            ;;
            
        *)
            echo "Uso: $0 {init|capture|create-session|list-sessions|focus|add-project|check-question|register-question|register-response|continuity-response|details|current-context}"
            echo ""
            echo "Comandos:"
            echo "  init                  - Inicializar sistema de memória compartilhada"
            echo "  capture               - Capturar contexto atual do sistema"
            echo "  create-session ID DESC - Criar nova sessão"
            echo "  list-sessions         - Listar sessões disponíveis"
            echo "  focus ID DESC         - Atualizar foco atual da sessão"
            echo "  add-project ID NAME PATH - Adicionar projeto ativo"
            echo "  check-question QUESTION - Verificar se é uma pergunta de continuidade"
            echo "  register-question ID Q - Registrar pergunta de continuidade"
            echo "  register-response ID FILE - Registrar resposta de continuidade"
            echo "  continuity-response ID - Gerar resposta de continuidade"
            echo "  details ID            - Mostrar detalhes da sessão"
            echo "  current-context       - Mostrar contexto atual"
            exit 1
            ;;
    esac
}

# Verificar parâmetros e executar
if [[ $# -lt 1 ]]; then
    echo "Uso: $0 {init|capture|create-session|list-sessions|focus|add-project|check-question|register-question|register-response|continuity-response|details|current-context}"
    exit 1
fi

main "$@"
