#!/bin/bash

# ================================================================================
# AUTO-CONTINUITY INTEGRADO COM SISTEMA DE EMERGÊNCIA
# Sistema completo de continuidade + recuperação + consolidação automática
# ================================================================================

set -euo pipefail

# Configurações globais
CONTINUITY_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY"
PROJECT_STATES_DIR="$CONTINUITY_DIR/project-states"
EMERGENCY_BACKUPS_DIR="$CONTINUITY_DIR/emergency-backups"
MEMORY_DIR="$CONTINUITY_DIR/memory"
LOGS_DIR="$CONTINUITY_DIR/logs"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Função para logging
log() {
    mkdir -p "$LOGS_DIR"
    echo -e "${CYAN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOGS_DIR/auto-continuity.log"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOGS_DIR/auto-continuity.log"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOGS_DIR/auto-continuity.log"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOGS_DIR/auto-continuity.log"
}

# Função para criar diretórios necessários
setup_directories() {
    local dirs=("$PROJECT_STATES_DIR" "$EMERGENCY_BACKUPS_DIR" "$MEMORY_DIR" "$LOGS_DIR")
    
    for dir in "${dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            log "Criado diretório: $dir"
        fi
    done
}

# Função de backup de emergência
emergency_backup() {
    local project_name="$1"
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_dir="$EMERGENCY_BACKUPS_DIR/${project_name}_emergency_${timestamp}"
    
    log "🚨 Iniciando backup de emergência para: $project_name"
    
    mkdir -p "$backup_dir"
    
    # Backup do estado atual do projeto
    if [[ -f "$PROJECT_STATES_DIR/$project_name.json" ]]; then
        cp "$PROJECT_STATES_DIR/$project_name.json" "$backup_dir/project_state.json"
        log_success "Estado do projeto salvo em backup de emergência"
    fi
    
    # Criar manifesto do backup
    cat > "$backup_dir/MANIFEST.txt" << EOF
BACKUP DE EMERGÊNCIA - $project_name
=====================================
Data/Hora: $(date)
Timestamp: $timestamp
Status: EMERGENCIAL

Conteúdo do Backup:
- project_state.json: Estado atual do projeto
- logs/: Logs da sessão atual

Este backup foi criado durante uma operação de emergência.
EOF
    
    # Backup dos logs
    if [[ -d "$LOGS_DIR" ]]; then
        cp -r "$LOGS_DIR" "$backup_dir/logs"
    fi
    
    log_success "🛡️ Backup de emergência completo: $backup_dir"
    echo "$backup_dir" > "$CONTINUITY_DIR/last_emergency_backup.txt"
}

# Função para verificar consistência entre memória e arquivos
check_memory_consistency() {
    local project_name="$1"
    
    log "🔍 Verificando consistência da memória para: $project_name"
    
    # Verificar se há discrepâncias entre timestamps
    local project_file="$PROJECT_STATES_DIR/$project_name.json"
    local memory_check_needed=false
    
    if [[ -f "$project_file" ]]; then
        local file_timestamp=$(stat -f "%m" "$project_file" 2>/dev/null || echo "0")
        local current_timestamp=$(date +%s)
        local time_diff=$((current_timestamp - file_timestamp))
        
        # Se arquivo foi modificado há mais de 1 hora, verificar memória
        if [[ $time_diff -gt 3600 ]]; then
            log_warning "Arquivo de estado antigo detectado (${time_diff}s). Verificação de memória necessária."
            memory_check_needed=true
        fi
    fi
    
    if [[ $memory_check_needed == true ]]; then
        return 0
    else
        return 1
    fi
}

# Função para limpar estados obsoletos
cleanup_obsolete_states() {
    local project_name="$1"
    
    log "🧹 Limpando estados obsoletos para: $project_name"
    
    # Remover backups antigos (manter apenas os 3 mais recentes)
    if [[ -d "$EMERGENCY_BACKUPS_DIR" ]]; then
        find "$EMERGENCY_BACKUPS_DIR" -name "${project_name}_emergency_*" -type d | sort -r | tail -n +4 | while read backup_dir; do
            log "Removendo backup antigo: $backup_dir"
            rm -rf "$backup_dir"
        done
    fi
    
    # Limpar logs antigos (manter apenas 7 dias)
    if [[ -d "$LOGS_DIR" ]]; then
        find "$LOGS_DIR" -name "*.log" -mtime +7 -delete 2>/dev/null || true
    fi
}

# Função principal integrada
main() {
    local PROJECT_NAME="$1"
    local ACTION="$2"
    
    # Setup inicial
    setup_directories
    
    # Verificar se projeto existe
    local PROJECT_FILE="$PROJECT_STATES_DIR/$PROJECT_NAME.json"
    
    if [[ -z "$PROJECT_NAME" ]] || [[ -z "$ACTION" ]]; then
        echo "Uso: $0 <projeto> <init|session-start|session-end|emergency-save|recovery>"
        echo ""
        echo "Projetos disponíveis:"
        ls -1 "$PROJECT_STATES_DIR"/*.json 2>/dev/null | sed 's/.*\///; s/\.json$//' | grep -v "project-template" || echo "Nenhum projeto encontrado"
        exit 1
    fi
    
    case "$ACTION" in
        "init")
            echo "🚀 Inicializando projeto completo: $PROJECT_NAME"
            
            # Backup de emergência se projeto já existir
            if [[ -f "$PROJECT_FILE" ]]; then
                emergency_backup "$PROJECT_NAME"
                log_warning "Projeto existente - backup criado antes da reinicialização"
            fi
            
            # 1. Desktop Commander: Criar estrutura
            "$CONTINUITY_DIR/continuity-manager.sh" "$PROJECT_NAME" init
            
            # 2. Capturar contexto inicial do sistema
            echo "📱 Contexto do sistema capturado"
            ps aux | head -20 > "$LOGS_DIR/${PROJECT_NAME}_init_processes.log"
            
            log_success "✅ Projeto $PROJECT_NAME totalmente inicializado!"
            ;;
            
        "session-start")
            echo "🔄 Iniciando sessão de trabalho: $PROJECT_NAME"
            
            # Verificar consistência da memória
            if check_memory_consistency "$PROJECT_NAME"; then
                log_warning "Possível inconsistência detectada - executando verificação completa"
                
                # Backup preventivo
                emergency_backup "$PROJECT_NAME"
                
                # Limpar estados obsoletos
                cleanup_obsolete_states "$PROJECT_NAME"
            fi

            # 1. Carregar estado anterior
            echo "📂 Carregando estado anterior:"
            if [[ -f "$PROJECT_FILE" ]]; then
                "$CONTINUITY_DIR/continuity-manager.sh" "$PROJECT_NAME" load
            else
                log_warning "Estado não encontrado. Será necessário inicializar primeiro."
                exit 1
            fi
            
            # 2. Capturar contexto atual do sistema
            echo "📱 Contexto atual capturado"
            ps aux | head -20 > "$LOGS_DIR/${PROJECT_NAME}_start_processes.log"
            
            # 3. Verificar se há missões críticas pendentes
            local critical_files=($(ls "$PROJECT_STATES_DIR"/${PROJECT_NAME}_critical_*.json 2>/dev/null || true))
            if [[ ${#critical_files[@]} -gt 0 ]]; then
                log_warning "🚨 MISSÕES CRÍTICAS PENDENTES DETECTADAS:"
                for critical_file in "${critical_files[@]}"; do
                    echo "   - $(basename "$critical_file")"
                done
            fi
            
            log_success "✅ Sessão iniciada! Pronto para continuar desenvolvimento."
            ;;
            
        "session-end")
            echo "💾 Finalizando sessão: $PROJECT_NAME"
            
            # 1. Salvar estado atual
            "$CONTINUITY_DIR/continuity-manager.sh" "$PROJECT_NAME" save
            
            # 2. Backup automático
            emergency_backup "$PROJECT_NAME"
            
            # 3. Capturar contexto final
            echo "📱 Contexto final preservado"
            ps aux | head -20 > "$LOGS_DIR/${PROJECT_NAME}_end_processes.log"
            
            # 4. Limpar estados antigos
            cleanup_obsolete_states "$PROJECT_NAME"
            
            log_success "✅ Sessão finalizada! Estado preservado para próxima vez."
            ;;

        "emergency-save")
            echo "🚨 SALVAMENTO DE EMERGÊNCIA: $PROJECT_NAME"
            
            # Executar salvamento de emergência completo
            emergency_backup "$PROJECT_NAME"
            
            # Finalizar sessão atual
            "$CONTINUITY_DIR/continuity-manager.sh" "$PROJECT_NAME" save 2>/dev/null || true
            
            log_success "🛡️ SALVAMENTO DE EMERGÊNCIA COMPLETO!"
            ;;
            
        "recovery")
            echo "🔄 MODO RECUPERAÇÃO: $PROJECT_NAME"
            
            # Verificar se há backups de emergência
            local latest_backup=$(ls -1t "$EMERGENCY_BACKUPS_DIR"/${PROJECT_NAME}_emergency_* 2>/dev/null | head -1 || true)
            
            if [[ -n "$latest_backup" ]]; then
                echo "📋 Backup de emergência encontrado: $latest_backup"
                cat "$latest_backup/MANIFEST.txt" 2>/dev/null || echo "Manifesto não encontrado"
                echo ""
            fi
            
            # Verificar missões críticas
            local critical_files=($(ls "$PROJECT_STATES_DIR"/${PROJECT_NAME}_critical_*.json 2>/dev/null || true))
            if [[ ${#critical_files[@]} -gt 0 ]]; then
                echo "🚨 MISSÕES CRÍTICAS IDENTIFICADAS:"
                for critical_file in "${critical_files[@]}"; do
                    echo "📋 $(basename "$critical_file")"
                done
                echo ""
            fi
            
            # Executar session-start automático
            echo "🎯 INICIANDO RECUPERAÇÃO AUTOMÁTICA..."
            "$0" "$PROJECT_NAME" session-start
            
            log_success "🎉 RECOVERY EXECUTADO COM SUCESSO"
            ;;
            
        *)
            log_error "❌ Ação inválida. Use: init, session-start, session-end, emergency-save, recovery"
            exit 1
            ;;
    esac
}

# Verificar parâmetros e executar
if [[ $# -lt 2 ]]; then
    echo "Uso: $0 <projeto> <acao>"
    echo ""
    echo "Ações disponíveis:"
    echo "  init          - Inicializar novo projeto"
    echo "  session-start - Iniciar sessão de trabalho"
    echo "  session-end   - Finalizar sessão"
    echo "  emergency-save - Salvamento de emergência"
    echo "  recovery      - Modo recuperação"
    echo ""
    echo "Projetos disponíveis:"
    ls -1 /Users/lucascardoso/apps/MCP/CONTINUITY/project-states/*.json 2>/dev/null | sed 's/.*\///; s/\.json$//' | grep -v "project-template" || echo "Nenhum projeto encontrado"
    exit 1
fi

# Executar backup automático antes de qualquer operação (exceto recovery)
if [[ "$2" != "recovery" ]]; then
    "$CONTINUITY_DIR/auto-backup.sh" "$1" 2>/dev/null || true
fi

# Executar função principal
main "$@"
