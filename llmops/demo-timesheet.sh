#!/bin/bash
#
# Demo do LLM Timesheet
# Este script demonstra o funcionamento do sistema de timesheet de LLMs
#

set -e

# Diretório base
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Funções de utilidade
print_header() {
    echo -e "\n${BLUE}===== $1 =====${NC}\n"
}

print_step() {
    echo -e "${CYAN}>> $1${NC}"
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
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 não encontrado. Por favor, instale o Python 3 antes de continuar."
    exit 1
fi

# Criar diretórios temporários para a demo
TEMP_DIR="$PARENT_DIR/temp_demo"
TIMESHEET_DIR="$TEMP_DIR/llmops/timesheets"
SPRINTS_DIR="$TEMP_DIR/llmops/sprints"
REPORTS_DIR="$TEMP_DIR/llmops/reports"

mkdir -p "$TIMESHEET_DIR" "$SPRINTS_DIR" "$REPORTS_DIR"

# Configurar ambiente temporário para a demo
export PYTHONPATH="$PARENT_DIR:$PYTHONPATH"

# Copiar llm_timesheet.py para o ambiente temporário
cp "$SCRIPT_DIR/llm_timesheet.py" "$TEMP_DIR/llmops/"

# Criar script de execução para a demo
cat > "$TEMP_DIR/llm-timesheet" << 'EOL'
#!/usr/bin/env python3

import os
import sys
import argparse
from llmops.llm_timesheet import main

if __name__ == "__main__":
    # Executar CLI do timesheet
    main()
EOL

chmod +x "$TEMP_DIR/llm-timesheet"

# Configurar diretório da demo
cd "$TEMP_DIR"

# Criar arquivo de configuração
cat > "$TEMP_DIR/llmops/config.json" << EOL
{
  "project_name": "demo-project",
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

# Criar alguns arquivos de exemplo para a demo
mkdir -p "$TEMP_DIR/src"
mkdir -p "$TEMP_DIR/docs"
mkdir -p "$TEMP_DIR/config"

# Arquivo Python de exemplo
cat > "$TEMP_DIR/src/example.py" << EOL
def hello_world():
    """Função de exemplo para a demo"""
    print("Hello from LLM Timesheet!")

if __name__ == "__main__":
    hello_world()
EOL

# Arquivo README de exemplo
cat > "$TEMP_DIR/README.md" << EOL
# Demo Project

Este é um projeto de exemplo para a demo do LLM Timesheet.
EOL

# Arquivo de configuração de exemplo
cat > "$TEMP_DIR/config/settings.json" << EOL
{
  "name": "demo-project",
  "version": "1.0.0",
  "description": "Projeto de exemplo para a demo do LLM Timesheet"
}
EOL

# Executar a demo
print_header "Demo do LLM Timesheet"
echo "Esta demo demonstra o funcionamento do sistema de timesheet de LLMs."
echo "Vamos simular um fluxo de trabalho típico com LLMs."
echo ""

# Etapa 1: Iniciar uma tarefa para o Claude
print_step "Iniciando uma tarefa para o Claude..."
TASK_ID_1=$(./llm-timesheet punch-in --llm "claude" --task "Implementar funcionalidade de hello world" | grep -o 'ID: [a-f0-9-]*' | cut -d' ' -f2)
print_success "Tarefa iniciada com ID: $TASK_ID_1"

# Simular modificação de arquivos
sleep 2
echo "# Esta função foi implementada pelo Claude" >> "$TEMP_DIR/src/example.py"
print_step "Claude modificou src/example.py"

# Etapa 2: Finalizar a tarefa do Claude
print_step "Finalizando a tarefa do Claude..."
./llm-timesheet punch-out --task-id "$TASK_ID_1" --summary "Implementei a funcionalidade de hello world com comentários" --detect-files
print_success "Tarefa do Claude finalizada"

# Etapa 3: Iniciar uma tarefa para o GPT-4
print_step "Iniciando uma tarefa para o GPT-4..."
TASK_ID_2=$(./llm-timesheet punch-in --llm "gpt-4" --task "Adicionar documentação ao projeto" | grep -o 'ID: [a-f0-9-]*' | cut -d' ' -f2)
print_success "Tarefa iniciada com ID: $TASK_ID_2"

# Simular modificação de arquivos
sleep 2
cat > "$TEMP_DIR/docs/usage.md" << EOL
# Como Usar

Esta é a documentação de uso do projeto demo.

## Funções

- \`hello_world()\`: Exibe uma mensagem de boas-vindas
EOL
print_step "GPT-4 criou docs/usage.md"

# Etapa 4: Finalizar a tarefa do GPT-4
print_step "Finalizando a tarefa do GPT-4..."
./llm-timesheet punch-out --task-id "$TASK_ID_2" --summary "Adicionei documentação básica de uso" --detect-files
print_success "Tarefa do GPT-4 finalizada"

# Etapa 5: Iniciar uma tarefa para o Gemini
print_step "Iniciando uma tarefa para o Gemini..."
TASK_ID_3=$(./llm-timesheet punch-in --llm "gemini" --task "Atualizar configurações do projeto" | grep -o 'ID: [a-f0-9-]*' | cut -d' ' -f2)
print_success "Tarefa iniciada com ID: $TASK_ID_3"

# Simular modificação de arquivos
sleep 2
cat > "$TEMP_DIR/config/settings.json" << EOL
{
  "name": "demo-project",
  "version": "1.0.1",
  "description": "Projeto de exemplo para a demo do LLM Timesheet",
  "author": "Gemini",
  "license": "MIT"
}
EOL
print_step "Gemini atualizou config/settings.json"

# Etapa 6: Finalizar a tarefa do Gemini
print_step "Finalizando a tarefa do Gemini..."
./llm-timesheet punch-out --task-id "$TASK_ID_3" --summary "Atualizei as configurações com informações de licença e autor" --detect-files
print_success "Tarefa do Gemini finalizada"

# Etapa 7: Gerar relatório do sprint
print_header "Gerando relatório do sprint"
./llm-timesheet report

# Etapa 8: Finalizar o sprint
print_header "Finalizando o sprint"
./llm-timesheet finish-sprint --summary "Sprint inicial com implementação básica, documentação e configuração"

# Limpar
print_header "Demo concluída"
echo "A demo foi concluída com sucesso."
echo "Os arquivos temporários estão em: $TEMP_DIR"
echo ""
echo "Para limpar os arquivos temporários, execute:"
echo "rm -rf $TEMP_DIR"
echo ""
echo "Para instalar o LLM Timesheet em seu projeto:"
echo "./llmops/install-llm-timesheet.sh /caminho/para/seu/projeto"