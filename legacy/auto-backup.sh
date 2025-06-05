#!/bin/bash

# Script de backup automático contra interrupções
# Executa a cada operação crítica para proteger progresso

PROJECT_NAME=$1
BACKUP_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Criar diretório de backup se não existir
mkdir -p "$BACKUP_DIR"

# Backup do estado do projeto
if [ -f "/Users/lucascardoso/apps/MCP/CONTINUITY/project-states/${PROJECT_NAME}.json" ]; then
    cp "/Users/lucascardoso/apps/MCP/CONTINUITY/project-states/${PROJECT_NAME}.json" \
       "$BACKUP_DIR/${PROJECT_NAME}_${TIMESTAMP}.json"
    echo "✅ Backup criado: ${PROJECT_NAME}_${TIMESTAMP}.json"
fi

# Manter apenas os 10 backups mais recentes por projeto
ls -t "$BACKUP_DIR/${PROJECT_NAME}_"*.json 2>/dev/null | tail -n +11 | xargs -r rm
echo "🧹 Backups antigos limpos (mantidos 10 mais recentes)"

# Log do backup
echo "$(date): Backup automático do projeto $PROJECT_NAME" >> "$BACKUP_DIR/backup.log"
