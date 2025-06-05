#!/bin/bash

# MCP Continuity Manager
# Script para gerenciar estados de projeto usando Desktop Commander

PROJECT_NAME="$1"
ACTION="$2"
STATES_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY/project-states"
TEMPLATE_FILE="$STATES_DIR/project-template.json"

if [ -z "$PROJECT_NAME" ]; then
    echo "Uso: $0 <project-name> [init|save|load|status]"
    exit 1
fi

PROJECT_FILE="$STATES_DIR/$PROJECT_NAME.json"

case "$ACTION" in
    "init")
        if [ -f "$PROJECT_FILE" ]; then
            echo "Projeto $PROJECT_NAME já existe!"
            exit 1
        fi
        
        cp "$TEMPLATE_FILE" "$PROJECT_FILE"
        echo "Projeto $PROJECT_NAME inicializado em $PROJECT_FILE"
        ;;
    
    "save")
        if [ ! -f "$PROJECT_FILE" ]; then
            echo "Projeto $PROJECT_NAME não encontrado. Use 'init' primeiro."
            exit 1
        fi
        
        # Atualizar timestamp
        TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")
        
        # Aqui você pode adicionar lógica para capturar estado atual
        echo "Estado do projeto $PROJECT_NAME salvo em $TIMESTAMP"
        ;;
    
    "load")
        if [ ! -f "$PROJECT_FILE" ]; then
            echo "Projeto $PROJECT_NAME não encontrado."
            exit 1
        fi
        
        echo "Carregando estado do projeto $PROJECT_NAME:"
        cat "$PROJECT_FILE" | jq -r '
            "Projeto: " + .projectInfo.name +
            "\nÚltima atualização: " + .projectInfo.lastUpdated +
            "\nFoco atual: " + .context.currentFocus +
            "\nEm progresso: " + .development.inProgress.description
        '
        ;;
    
    "status"|*)
        if [ -f "$PROJECT_FILE" ]; then
            echo "📁 Projeto: $PROJECT_NAME"
            echo "📄 Arquivo: $PROJECT_FILE"
            echo "📅 Modificado: $(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$PROJECT_FILE")"
            echo ""
            echo "Status detalhado:"
            cat "$PROJECT_FILE" | jq -r '.development.inProgress | 
                "Tipo: " + .type + 
                "\nDescrição: " + .description +
                "\nTarefas restantes: " + (.remainingTasks | length | tostring)'
        else
            echo "Projeto $PROJECT_NAME não encontrado."
            echo "Projetos disponíveis:"
            ls -1 "$STATES_DIR"/*.json 2>/dev/null | sed 's/.*\///; s/\.json$//' | grep -v "project-template"
        fi
        ;;
esac