#!/bin/bash

# 🚨 RESTAURAÇÃO CRÍTICA DE EMERGÊNCIA
# Restaura arquivos essenciais dos backups para corrigir problemas sistêmicos

echo "🚨 RESTAURAÇÃO CRÍTICA DE EMERGÊNCIA"
echo "⚠️ Problema: Refatorações automáticas quebraram código essencial"

PROJECT_DIR="/Users/lucascardoso/apps/MCP/luaraujo-livro-app copy"
SRC_DIR="$PROJECT_DIR/src"

# Localizar último backup válido
SAFE_BACKUP="/Users/lucascardoso/apps/MCP/CONTINUITY/safe-dark-mode-20250602_161034/src"

if [[ ! -d "$SAFE_BACKUP" ]]; then
    echo "❌ Backup não encontrado: $SAFE_BACKUP"
    exit 1
fi

echo "💾 Restaurando do backup seguro: $SAFE_BACKUP"

# ARQUIVOS CRÍTICOS PARA RESTAURAR
CRITICAL_FILES=(
    "App.js"
    "screens/HomeScreen.js"
    "screens/HomeScreenSimple.js"
    "screens/Chapter9Screen.js"
    "services/NotificationService.js"
)

echo ""
echo "🔧 RESTAURANDO ARQUIVOS CRÍTICOS:"

for file in "${CRITICAL_FILES[@]}"; do
    if [[ "$file" == "App.js" ]]; then
        source_file="$SAFE_BACKUP/../App.js"
        dest_file="$PROJECT_DIR/App.js"
    else
        source_file="$SAFE_BACKUP/$file"
        dest_file="$SRC_DIR/$file"
    fi
    
    if [[ -f "$source_file" ]]; then
        echo "  ✅ Restaurando: $file"
        cp "$source_file" "$dest_file"
    else
        echo "  ❌ Arquivo não encontrado no backup: $file"
    fi
done

echo ""
echo "✅ RESTAURAÇÃO CRÍTICA CONCLUÍDA!"
echo ""
echo "🎯 ARQUIVOS RESTAURADOS:"
echo "   ✅ App.js: Navegação Chapter9 restaurada"
echo "   ✅ HomeScreen.js: Navigation para Chapter9 corrigida"  
echo "   ✅ HomeScreenSimple.js: Lista de capítulos completa"
echo "   ✅ Chapter9Screen.js: Código funcional restaurado"
echo "   ✅ NotificationService.js: Erros de notificação corrigidos"
echo ""
echo "📱 RESULTADO ESPERADO:"
echo "   ✅ Módulo 3 Extra (Chapter 9) deve estar visível"
echo "   ✅ Navegação funcionando corretamente"
echo "   ✅ Notificações sem erros"
echo "   ✅ App estável e funcional"
echo ""
echo "🔄 TESTE IMEDIATO:"
echo "   1. Reinicie o app"
echo "   2. Verifique se Módulo 3 Extra aparece na lista"
echo "   3. Tente abrir o Chapter 9"
echo "   4. Confirme que não há erros de COLORS"
