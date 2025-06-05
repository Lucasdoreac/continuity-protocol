#!/bin/bash

# Script para corrigir hardcoding sistemático no app
# Remove cores hardcoded e adiciona useTheme onde necessário

APP_DIR="/Users/lucascardoso/apps/MCP/luaraujo-livro-app copy/src"
BACKUP_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY/hardcoding-backup-$(date +%Y%m%d_%H%M%S)"

echo "🚀 CORREÇÃO SISTEMÁTICA DE HARDCODING"
echo "======================================"

# 1. Criar backup
echo "📦 Criando backup..."
mkdir -p "$BACKUP_DIR"
cp -r "$APP_DIR" "$BACKUP_DIR/"

# 2. Função para adicionar useTheme a um arquivo
add_useTheme() {
    local file="$1"
    
    # Verificar se já tem useTheme
    if grep -q "useTheme\|useColors" "$file"; then
        echo "  ✅ $file - já tem useTheme"
        return 0
    fi
    
    # Verificar se tem import React
    if ! grep -q "import React" "$file"; then
        echo "  ❌ $file - não é componente React"
        return 1
    fi
    
    # Verificar se tem hardcoding
    if ! grep -q "#[0-9a-fA-F]\{3,6\}\|backgroundColor.*white\|color.*black" "$file"; then
        echo "  ⚪ $file - sem hardcoding detectado"
        return 1
    fi
    
    echo "  🔧 $file - corrigindo..."    
    # Adicionar import useTheme após outros imports React
    sed -i '' '/import.*react-native/a\
import { useTheme } from '\''../contexts/ThemeContext'\'';
' "$file"
    
    # Adicionar const { colors } = useTheme(); após definição do componente
    sed -i '' '/const.*= () => {/a\
  const { colors } = useTheme();
' "$file"
    
    # Correções comuns de cores
    sed -i '' 's/backgroundColor.*white/backgroundColor: colors.background/g' "$file"
    sed -i '' 's/backgroundColor.*#ffffff/backgroundColor: colors.background/g' "$file"
    sed -i '' 's/color.*black/color: colors.text/g' "$file"
    sed -i '' 's/color.*#000000/color: colors.text/g' "$file"
    sed -i '' 's/color.*white/color: colors.white/g' "$file"
    sed -i '' 's/shadowColor.*#000/shadowColor: colors.shadow/g' "$file"
    
    return 0
}

# 3. Corrigir componentes mais críticos primeiro
echo "🎯 Corrigindo componentes críticos..."

critical_files=(
    "components/InteractiveTips.js"
    "screens/Chapter7Screen.js"
    "screens/HomeScreen.js"
    "screens/Chapter6Screen.js"
    "screens/Chapter9Screen.js"
    "screens/Chapter8Screen.js"
    "screens/Chapter5Screen.js"
    "components/TaxCalculator.js"
)

for file in "${critical_files[@]}"; do
    full_path="$APP_DIR/$file"
    if [ -f "$full_path" ]; then
        add_useTheme "$full_path"
    else
        echo "  ⚠️  $file - não encontrado"
    fi
done

echo ""
echo "✅ Backup criado em: $BACKUP_DIR"
echo "✅ Correções aplicadas aos componentes críticos"
echo ""
echo "🧪 TESTE O APP: npx expo start"
echo "   Se houver problemas, restaure: cp -r $BACKUP_DIR/src/* $APP_DIR/"
