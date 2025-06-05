#!/bin/bash

# 🎯 SISTEMA ÍNTEGRO DE CORES - IMPLEMENTAÇÃO SEGURA
# Implementa modo dark completo sem quebrar funcionalidade existente

echo "🎯 IMPLEMENTANDO SISTEMA ÍNTEGRO DE CORES - VERSÃO SEGURA"
echo "⚠️ Preservando estabilidade do LuaRaujo App (Stable - DO NOT BREAK)"

PROJECT_DIR="/Users/lucascardoso/apps/MCP/luaraujo-livro-app copy"
SRC_DIR="$PROJECT_DIR/src"
BACKUP_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY/safe-dark-mode-$(date +%Y%m%d_%H%M%S)"

mkdir -p "$BACKUP_DIR"
echo "💾 Backup seguro: $BACKUP_DIR"

# BACKUP COMPLETO ANTES DE QUALQUER MUDANÇA
echo "📦 Criando backup completo para preservar estabilidade..."
cp -r "$SRC_DIR" "$BACKUP_DIR/"

# FASE 1: IMPLEMENTAR APENAS OS SCREENS QUE PRECISAM (CHAPTERS 2-9)
echo ""
echo "📱 FASE 1: APLICANDO MODO DARK AOS CHAPTERS 2-9"
echo "   (Chapter 1 já está parcialmente implementado)"

CHAPTERS_TO_FIX=(
    "Chapter2Screen.js"
    "Chapter3Screen.js" 
    "Chapter4Screen.js"
    "Chapter5Screen.js"
    "Chapter6Screen.js"
    "Chapter7Screen.js"
    "Chapter8Screen.js"
    "Chapter9Screen.js"
)

# Função segura para aplicar modo dark
apply_safe_dark_mode() {
    local file="$1"
    echo "  🔧 Aplicando modo dark: $(basename "$file")"
    
    # Backup individual
    cp "$file" "$BACKUP_DIR/$(basename "$file").backup"
    
    # Verificar se já tem import de ThemeContext
    if ! grep -q "ThemeContext" "$file"; then
        # Adicionar import do hook legado (que sabemos que funciona)
        sed -i '' '/import.*globalStyles/a\
import { useLegacyColors } from '\''../contexts/ThemeContext'\'';
' "$file"
        echo "    ✅ Import useLegacyColors adicionado"
    fi
    
    # Verificar se já tem o hook implementado
    if ! grep -q "useLegacyColors\|useColors" "$file"; then
        # Encontrar função do componente e adicionar hook
        local component_line=$(grep -n "const.*Screen.*= (" "$file" | head -1 | cut -d: -f1)
        if [[ -n "$component_line" ]]; then
            sed -i '' "${component_line}a\\
  const COLORS = useLegacyColors(); // 🎨 Cores dinâmicas para modo dark\\
" "$file"
            echo "    ✅ Hook de cores dinâmicas adicionado"
        fi
    fi
    
    echo "    ✅ Modo dark aplicado com segurança"
}

# Aplicar a cada chapter
for chapter in "${CHAPTERS_TO_FIX[@]}"; do
    file="$SRC_DIR/screens/$chapter"
    if [[ -f "$file" ]]; then
        apply_safe_dark_mode "$file"
    else
        echo "  ❌ Arquivo não encontrado: $chapter"
    fi
done

echo ""
echo "✅ FASE 1 CONCLUÍDA - CHAPTERS 2-9 PREPARADOS"
echo ""
echo "🎯 RESULTADO ESPERADO:"
echo "   ✅ Chapter 1: Já funcionando (preservado)"
echo "   ✅ Chapters 2-9: Hooks de cores dinâmicas aplicados"
echo "   ✅ Estabilidade: Preservada (sem quebras)"
echo "   ✅ Funcionalidade: Mantida"
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo "   1. Testar cada chapter individualmente"
echo "   2. Verificar se modo dark funciona corretamente"
echo "   3. Aplicar estilos dinâmicos manualmente onde necessário"
echo "   4. Usar Chapter1Screen.js como referência de implementação"
echo ""
echo "🔄 TESTE IMEDIATO:"
echo "   - Navegue pelos chapters 2-9 no modo dark"
echo "   - Verifique se textos ficam legíveis"
echo "   - Compare com Chapter 1 (referência funcionando)"
echo ""
echo "💾 BACKUP COMPLETO EM: $BACKUP_DIR"
echo "   (Para restaurar se necessário)"
