#!/bin/bash
#
# Instalador do LLM Timesheet
# Este script configura o sistema de timesheet de LLMs em qualquer projeto
#

set -e

# Diretório base do sistema de timesheet
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTINUITY_DIR="$(dirname "$SCRIPT_DIR")"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções de utilidade
print_header() {
    echo -e "\n${BLUE}===== $1 =====${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar se o Python está instalado
check_python() {
    print_header "Verificando requisitos"
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 não encontrado. Por favor, instale o Python 3 antes de continuar."
        exit 1
    fi
    
    print_success "Python 3 encontrado: $(python3 --version)"
    
    # Verificar dependências Python
    PY_DEPS=("uuid" "pathlib" "datetime" "typing" "json" "logging" "argparse" "hashlib" "re" "subprocess")
    MISSING_DEPS=()
    
    for dep in "${PY_DEPS[@]}"; do
        if ! python3 -c "import $dep" &> /dev/null; then
            MISSING_DEPS+=("$dep")
        fi
    done
    
    if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
        print_warning "Algumas dependências Python podem estar faltando: ${MISSING_DEPS[*]}"
        print_warning "O script tentará continuar, mas podem ocorrer erros."
    else
        print_success "Todas as dependências Python necessárias estão instaladas."
    fi
}

# Configurar diretórios do timesheet no projeto alvo
setup_directories() {
    print_header "Configurando diretórios"
    
    TARGET_DIR="$1"
    
    # Diretórios a serem criados
    DIRS=(
        "$TARGET_DIR/llmops"
        "$TARGET_DIR/llmops/timesheets"
        "$TARGET_DIR/llmops/sprints"
        "$TARGET_DIR/llmops/reports"
    )
    
    for dir in "${DIRS[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_success "Diretório criado: $dir"
        else
            print_warning "Diretório já existe: $dir"
        fi
    done
}

# Copiar arquivos necessários
copy_files() {
    print_header "Copiando arquivos"
    
    TARGET_DIR="$1"
    
    # Arquivos a serem copiados
    FILES=(
        "$SCRIPT_DIR/llm_timesheet.py"
        "$SCRIPT_DIR/llm-timesheet-mcp.py"
    )
    
    for file in "${FILES[@]}"; do
        filename=$(basename "$file")
        if [ -f "$file" ]; then
            cp "$file" "$TARGET_DIR/llmops/"
            print_success "Arquivo copiado: $filename"
        else
            print_error "Arquivo não encontrado: $file"
        fi
    done
    
    # Criar links simbólicos para os scripts
    ln -sf "$TARGET_DIR/llmops/llm_timesheet.py" "$TARGET_DIR/llm-timesheet"
    chmod +x "$TARGET_DIR/llm-timesheet"
    print_success "Link simbólico criado: llm-timesheet"
}

# Criar configuração inicial
create_config() {
    print_header "Criando configuração"
    
    TARGET_DIR="$1"
    PROJECT_NAME=$(basename "$TARGET_DIR")
    
    CONFIG_FILE="$TARGET_DIR/llmops/config.json"
    
    if [ ! -f "$CONFIG_FILE" ]; then
        cat > "$CONFIG_FILE" << EOL
{
  "project_name": "$PROJECT_NAME",
  "current_sprint": "sprint-1",
  "sprint_duration_days": 7,
  "known_llms": ["claude", "gpt-4", "gemini", "llama"],
  "timesheet_format": "json",
  "auto_organize": true,
  "organization_rules": {
    "code": ["*.py", "*.js", "*.html", "*.css", "*.sh"],
    "documentation": ["*.md", "README*", "*.txt"],
    "configuration": ["*.json", "*.yml", "*.yaml", "*.toml"],
    "data": ["*.csv", "*.json", "*.xml"]
  }
}
EOL
        print_success "Arquivo de configuração criado: $CONFIG_FILE"
    else
        print_warning "Arquivo de configuração já existe: $CONFIG_FILE"
    fi
}

# Criar script auxiliar para início rápido
create_helper_script() {
    print_header "Criando script auxiliar"
    
    TARGET_DIR="$1"
    
    HELPER_SCRIPT="$TARGET_DIR/llm-punch.sh"
    
    cat > "$HELPER_SCRIPT" << 'EOL'
#!/bin/bash
#
# LLM Punch - Script auxiliar para o sistema de timesheet de LLMs
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TIMESHEET_SCRIPT="$SCRIPT_DIR/llm-timesheet"

# Verificar se o script principal existe
if [ ! -f "$TIMESHEET_SCRIPT" ]; then
    echo "❌ Script principal não encontrado: $TIMESHEET_SCRIPT"
    exit 1
fi

# Verificar se o argumento foi fornecido
if [ "$1" == "in" ]; then
    if [ -z "$2" ] || [ -z "$3" ]; then
        echo "❌ Uso: $0 in <llm_name> <task_description>"
        exit 1
    fi
    
    LLM_NAME="$2"
    shift 2
    TASK_DESC="$*"
    
    # Executar punch-in
    TASK_ID=$("$TIMESHEET_SCRIPT" punch-in --llm "$LLM_NAME" --task "$TASK_DESC" | grep -o 'ID: [a-f0-9-]*' | cut -d' ' -f2)
    
    if [ -n "$TASK_ID" ]; then
        echo "$TASK_ID" > "$SCRIPT_DIR/.current_task"
        echo "✅ Tarefa iniciada com ID: $TASK_ID"
        echo "💡 Para finalizar, execute: $0 out \"Resumo do trabalho\""
    else
        echo "❌ Erro ao iniciar tarefa"
        exit 1
    fi
    
elif [ "$1" == "out" ]; then
    if [ -z "$2" ]; then
        echo "❌ Uso: $0 out <summary>"
        exit 1
    fi
    
    shift
    SUMMARY="$*"
    
    # Verificar se há uma tarefa atual
    if [ ! -f "$SCRIPT_DIR/.current_task" ]; then
        echo "❌ Nenhuma tarefa em andamento"
        echo "💡 Inicie uma tarefa com: $0 in <llm_name> <task_description>"
        exit 1
    fi
    
    TASK_ID=$(cat "$SCRIPT_DIR/.current_task")
    
    # Executar punch-out
    "$TIMESHEET_SCRIPT" punch-out --task-id "$TASK_ID" --summary "$SUMMARY" --detect-files
    
    # Limpar tarefa atual
    rm "$SCRIPT_DIR/.current_task"
    
elif [ "$1" == "report" ]; then
    # Gerar relatório
    "$TIMESHEET_SCRIPT" report
    
elif [ "$1" == "finish" ]; then
    if [ -z "$2" ]; then
        echo "❌ Uso: $0 finish <sprint_summary>"
        exit 1
    fi
    
    shift
    SUMMARY="$*"
    
    # Finalizar sprint
    "$TIMESHEET_SCRIPT" finish-sprint --summary "$SUMMARY"
    
else
    echo "LLM Punch - Script auxiliar para o sistema de timesheet de LLMs"
    echo ""
    echo "Uso:"
    echo "  $0 in <llm_name> <task_description>  # Iniciar uma tarefa"
    echo "  $0 out <summary>                     # Finalizar a tarefa atual"
    echo "  $0 report                            # Gerar relatório do sprint atual"
    echo "  $0 finish <sprint_summary>           # Finalizar o sprint atual"
    echo ""
    echo "Exemplo:"
    echo "  $0 in claude \"Implementar feature X\""
    echo "  # ... trabalho realizado ..."
    echo "  $0 out \"Implementei a feature X com testes\""
fi
EOL
    
    chmod +x "$HELPER_SCRIPT"
    print_success "Script auxiliar criado: $HELPER_SCRIPT"
}

# Função principal
main() {
    print_header "Instalador do LLM Timesheet"
    
    # Verificar argumento de diretório de destino
    if [ -z "$1" ]; then
        TARGET_DIR="$(pwd)"
        print_warning "Nenhum diretório especificado, usando o diretório atual: $TARGET_DIR"
    else
        TARGET_DIR="$1"
        
        # Verificar se o diretório existe
        if [ ! -d "$TARGET_DIR" ]; then
            print_error "Diretório não encontrado: $TARGET_DIR"
            exit 1
        fi
    fi
    
    # Verificar requisitos
    check_python
    
    # Configurar diretórios
    setup_directories "$TARGET_DIR"
    
    # Copiar arquivos
    copy_files "$TARGET_DIR"
    
    # Criar configuração
    create_config "$TARGET_DIR"
    
    # Criar script auxiliar
    create_helper_script "$TARGET_DIR"
    
    print_header "Instalação concluída"
    echo "O sistema de timesheet de LLMs foi instalado com sucesso em: $TARGET_DIR"
    echo ""
    echo "Para começar a usar:"
    echo "  1. Inicie uma tarefa: ./llm-punch.sh in <llm_name> <task_description>"
    echo "  2. Finalize a tarefa: ./llm-punch.sh out <summary>"
    echo "  3. Veja o relatório: ./llm-punch.sh report"
    echo ""
    echo "Para integração com MCP:"
    echo "  1. Importe o módulo 'llmops.llm_timesheet_mcp' no seu servidor MCP"
    echo "  2. Veja o exemplo em: $CONTINUITY_DIR/mcp-continuity-server-integrated.py"
}

# Executar
main "$@"