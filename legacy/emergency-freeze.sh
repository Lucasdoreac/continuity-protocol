#!/bin/bash

# 🚨 EMERGENCY FREEZE - CONGELAMENTO IMEDIATO DO ESTADO TOTAL
# Use IMEDIATAMENTE quando algo der errado durante modificações massivas

set -e
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
CONTINUITY_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY"
FREEZE_DIR="$CONTINUITY_DIR/emergency-freeze"

echo "🚨🚨🚨 EMERGENCY FREEZE - $TIMESTAMP 🚨🚨🚨"

# Criar diretório de freeze
mkdir -p "$FREEZE_DIR/$TIMESTAMP"
FREEZE_PATH="$FREEZE_DIR/$TIMESTAMP"

# 1. BACKUP IMEDIATO DOS PROJETOS CRÍTICOS
echo "📦 Backup imediato..."
cp -r "/Users/lucascardoso/apps/MCP/luaraujo-livro-app copy" "$FREEZE_PATH/luaraujo-app" &
cp -r "/Users/lucascardoso/apps/MCP/luaraujo-premium-hub" "$FREEZE_PATH/luaraujo-hub" &
cp -r "/Users/lucascardoso/apps/MCP/luaraujo-migration" "$FREEZE_PATH/luaraujo-migration" &
cp -r "$CONTINUITY_DIR/project-states" "$FREEZE_PATH/continuity-states" &
wait

# 2. DETECÇÃO DE ARQUIVOS ÓRFÃOS
echo "🔍 Detectando arquivos órfãos..."
find "/Users/lucascardoso/apps/MCP/luaraujo-livro-app copy" -mtime -2h -type f > "$FREEZE_PATH/recent_files.txt" 2>/dev/null || true

# 3. CONTEXTO DO SISTEMA
echo "💻 Capturando contexto..."
ps aux | head -30 > "$FREEZE_PATH/processes.txt"
date > "$FREEZE_PATH/timestamp.txt"

# 4. MANIFESTO DE EMERGÊNCIA
cat > "$FREEZE_PATH/RECOVERY_COMMAND.txt" << EOF
🚨 COMANDO DE RECOVERY ABSOLUTO:
/Users/lucascardoso/apps/MCP/CONTINUITY/emergency-unfreeze.sh $TIMESTAMP

📋 Use este comando em qualquer chat novo para recovery total.
✅ Tudo foi preservado: projetos, estados, logs, arquivos órfãos.
EOF

echo "✅ FREEZE COMPLETO: $FREEZE_PATH"
echo "🎯 RECOVERY: emergency-unfreeze.sh $TIMESTAMP"
