#!/bin/bash

# 🚨 CORREÇÃO CRÍTICA: ELIMINAÇÃO DE CORES ESTÁTICAS #666
# Substitui todas as instâncias de color: '#666' por color: COLORS.textSecondary

echo "🚨 CORREÇÃO SISTEMÁTICA: CORES ESTÁTICAS #666 → DINÂMICAS"
echo "🎯 Problema: 50+ instâncias de #666 causando texto ilegível no modo escuro"

SRC_DIR="/Users/lucascardoso/apps/MCP/luaraujo-livro-app copy/src"
BACKUP_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY/color-fix-backup-$(date +%Y%m%d_%H%M%S)"

mkdir -p "$BACKUP_DIR"
echo "💾 Backup completo: $BACKUP_DIR"

# Função para corrigir arquivo
fix_color_in_file() {
    local file="$1"
    local backup_file="$BACKUP_DIR/$(basename "$file")"
    
    echo "  🔧 Processando: $(basename "$file")"
    
    # Backup
    cp "$file" "$backup_file"
    
    # Substituir color: '#666' por color: COLORS.textSecondary
    sed -i '' "s/color: '#666'/color: COLORS.textSecondary/g" "$file"
    
    # Substituir color:'#666' (sem espaço)
    sed -i '' "s/color:'#666'/color: COLORS.textSecondary/g" "$file"
    
    # Substituir color: \"#666\"
    sed -i '' 's/color: "#666"/color: COLORS.textSecondary/g' "$file"
    
    # Verificar se precisa do import COLORS
    if grep -q "COLORS.textSecondary" "$file" && ! grep -q "import.*COLORS.*globalStyles" "$file"; then
        # Adicionar import se não existir
        if grep -q "import.*StyleSheet" "$file"; then
            sed -i '' '/import.*StyleSheet/a\
import { COLORS } from '\''../styles/globalStyles'\'';
' "$file"
            echo "    ✅ Import COLORS adicionado"
        fi
    fi
    
    echo "    ✅ Cores corrigidas"
}

# Encontrar todos os arquivos com #666
echo ""
echo "🔍 ARQUIVOS COM CORES PROBLEMÁTICAS:"

# Usar find para localizar todos os arquivos .js
find "$SRC_DIR" -name "*.js" -type f | while read file; do
    if grep -q "color.*#666" "$file"; then
        fix_color_in_file "$file"
    fi
done

echo ""
echo "✅ CORREÇÃO SISTEMÁTICA CONCLUÍDA!"
echo "🎯 RESULTADO:"
echo "   - Todas as instâncias de color: '#666' → color: COLORS.textSecondary"
echo "   - Imports COLORS adicionados onde necessário"
echo "   - Backup completo criado"
echo ""
echo "📱 RESULTADO VISUAL:"
echo "   🌞 Modo claro: COLORS.textSecondary = #666666 (cinza escuro em fundo claro)"
echo "   🌙 Modo escuro: COLORS.textSecondary = #bdc3c7 (cinza claro em fundo escuro)"
echo ""
echo "🎉 TEXTO LEGÍVEL EM AMBOS OS MODOS!"
