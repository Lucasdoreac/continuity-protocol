#!/bin/bash

# 🚨 EMERGENCY FREEZE - VERSÃO RÁPIDA (ANTI-TRAVAMENTO)
# Versão otimizada que evita timeouts

set -e
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
CONTINUITY_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY"
FREEZE_DIR="$CONTINUITY_DIR/emergency-freeze"

echo "🚨 EMERGENCY FREEZE RÁPIDO - $TIMESTAMP 🚨"

# Criar diretório de freeze
mkdir -p "$FREEZE_DIR/$TIMESTAMP"
FREEZE_PATH="$FREEZE_DIR/$TIMESTAMP"

# 1. BACKUP APENAS DOS ESTADOS (RÁPIDO)
echo "📦 Backup estados críticos..."
if [[ -d "$CONTINUITY_DIR/project-states" ]]; then
    cp -r "$CONTINUITY_DIR/project-states" "$FREEZE_PATH/continuity-states"
fi

# 2. BACKUP SELETIVO (só arquivos pequenos)
echo "📋 Backup arquivos pequenos..."
if [[ -d "/Users/lucascardoso/apps/MCP/luaraujo-migration" ]]; then
    cp -r "/Users/lucascardoso/apps/MCP/luaraujo-migration" "$FREEZE_PATH/luaraujo-migration"
fi

# 3. CONTEXTO SISTEMA (RÁPIDO)
echo "💻 Contexto sistema..."
ps aux | head -30 > "$FREEZE_PATH/processes.txt"
date > "$FREEZE_PATH/timestamp.txt"
echo "Freeze criado por emergency-freeze-fast.sh" > "$FREEZE_PATH/source.txt"

# 4. LISTA DE ARQUIVOS GRANDES (sem copiar)
echo "📊 Listando arquivos grandes..."
echo "ARQUIVOS GRANDES NÃO COPIADOS (para velocidade):" > "$FREEZE_PATH/large_files_skipped.txt"
du -sh "/Users/lucascardoso/apps/MCP/luaraujo-livro-app copy" 2>/dev/null >> "$FREEZE_PATH/large_files_skipped.txt" || echo "luaraujo-app: não encontrado" >> "$FREEZE_PATH/large_files_skipped.txt"
du -sh "/Users/lucascardoso/apps/MCP/luaraujo-premium-hub" 2>/dev/null >> "$FREEZE_PATH/large_files_skipped.txt" || echo "luaraujo-hub: não encontrado" >> "$FREEZE_PATH/large_files_skipped.txt"

# 5. MANIFESTO DE EMERGÊNCIA
cat > "$FREEZE_PATH/RECOVERY_COMMAND.txt" << EOF
🚨 COMANDO DE RECOVERY:
/Users/lucascardoso/apps/MCP/CONTINUITY/emergency-unfreeze.sh $TIMESTAMP

📋 FREEZE RÁPIDO - Estados críticos preservados
⚡ Arquivos grandes foram listados mas não copiados para velocidade
✅ Use este comando em qualquer chat para recovery
EOF

echo "✅ FREEZE RÁPIDO COMPLETO: $FREEZE_PATH"
echo "🎯 RECOVERY: emergency-unfreeze.sh $TIMESTAMP"
echo "⚡ Freeze otimizado - sem arquivos grandes"
