#!/bin/bash

# 🛠️ CORREÇÃO AUTOMÁTICA DE ACESSIBILIDADE - CAPÍTULOS LUARAUJO
# Corrige problema de texto invisível no tema escuro
# Baseado no padrão aplicado com sucesso no Chapter1Screen.js

PROJECT_DIR="/Users/lucascardoso/apps/MCP/luaraujo-livro-app copy/src/screens"
BACKUP_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY/chapter-backups-$(date +%Y%m%d_%H%M%S)"

echo "🔧 INICIANDO CORREÇÃO DE ACESSIBILIDADE DOS CAPÍTULOS"
echo "📂 Projeto: $PROJECT_DIR"

# Criar backup
mkdir -p "$BACKUP_DIR"
echo "💾 Criando backup em: $BACKUP_DIR"

# Lista dos capítulos a corrigir (Chapter1 já foi corrigido)
CHAPTERS=("Chapter2Screen.js" "Chapter3Screen.js" "Chapter4Screen.js" "Chapter5Screen.js" "Chapter6Screen.js" "Chapter7Screen.js" "Chapter8Screen.js" "Chapter9Screen.js")

for chapter in "${CHAPTERS[@]}"; do
    echo "🎯 Processando: $chapter"
    
    # Backup do arquivo original
    cp "$PROJECT_DIR/$chapter" "$BACKUP_DIR/"
    echo "  ✅ Backup criado"
    
    # Verificar se já usa useColors (para não corrigir duas vezes)
    if grep -q "useColors" "$PROJECT_DIR/$chapter"; then
        echo "  ⚠️  $chapter já usa useColors - pulando"
        continue
    fi
    
    echo "  🔧 Aplicando correção de acessibilidade..."
    
    # 1. Adicionar import do useColors
    sed -i '' '/import.*globalStyles/a\
import { useColors } from '\''../contexts/ThemeContext'\'';
' "$PROJECT_DIR/$chapter"
    
    echo "  ✅ Import do useColors adicionado"
    
    echo "  📝 Próximo passo: Implementar estilos dinâmicos manualmente"
    echo "      Pattern: const colors = useColors();"
    echo "      Pattern: backgroundColor: colors.background"
    echo "      Pattern: color: colors.text"
    echo ""
done

echo "🎉 CORREÇÃO PARCIAL CONCLUÍDA!"
echo "📋 Próximos passos manuais:"
echo "   1. Para cada capítulo, implementar estilos dinâmicos"
echo "   2. Padrão: Chapter1Screen.js (já corrigido)"
echo "   3. Testar acessibilidade no tema escuro"
echo ""
echo "📂 Backups salvos em: $BACKUP_DIR"
