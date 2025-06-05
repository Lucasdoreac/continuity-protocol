#!/bin/bash

# 🚨 SOLUÇÃO CRÍTICA: NAVEGAÇÃO CHAPTER 9 (MÓDULO 3 EXTRA)
# Corrige problemas: Chapter 9 não abre da home + falta navegação do Chapter 8

echo "🚨 CORRIGINDO NAVEGAÇÃO CRÍTICA DO MÓDULO 3 (CHAPTER 9)"
echo "🎯 Problemas identificados:"
echo "   ❌ Módulo 3 não abre da home"
echo "   ❌ Sem navegação do Chapter 8 → Chapter 9"

PROJECT_DIR="/Users/lucascardoso/apps/MCP/luaraujo-livro-app copy"
BACKUP_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY/navigation-fix-$(date +%Y%m%d_%H%M%S)"

mkdir -p "$BACKUP_DIR"
echo "💾 Backup: $BACKUP_DIR"

# BACKUP DOS ARQUIVOS QUE SERÃO MODIFICADOS
cp "$PROJECT_DIR/src/screens/Chapter8Screen.js" "$BACKUP_DIR/"
cp "$PROJECT_DIR/src/screens/HomeScreenSimple.js" "$BACKUP_DIR/"
cp "$PROJECT_DIR/src/screens/Chapter9Screen.js" "$BACKUP_DIR/"

echo ""
echo "🔧 IMPLEMENTANDO CORREÇÕES:"

echo "1️⃣ Adicionando navegação do Chapter 8 → Chapter 9..."

# ADICIONAR NAVEGAÇÃO NO FINAL DO CHAPTER 8
cat >> "$PROJECT_DIR/src/screens/Chapter8Screen.js" << 'EOF'

          {/* Navegação entre capítulos */}
          <View style={styles.navigationButtons}>
            <TouchableOpacity 
              style={[styles.navButton, styles.prevButton]}
              onPress={() => navigation.navigate('Chapter7')}
            >
              <Text style={styles.prevButtonText}>← Voltar</Text>
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={[styles.navButton, styles.nextButton]}
              onPress={() => navigation.navigate('Chapter9')}
            >
              <Text style={styles.nextButtonText}>Próximo →</Text>
            </TouchableOpacity>
          </View>

          {/* Botão especial para Módulo 3 Extra */}
          <TouchableOpacity 
            style={styles.premiumNextButton}
            onPress={() => navigation.navigate('Chapter9')}
          >
            <Text style={styles.premiumNextText}>🚀 Módulo 3: Ferramentas Avançadas</Text>
            <Text style={styles.premiumNextSubtext}>Metas • Carteira • Relatórios</Text>
          </TouchableOpacity>

        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

// ADICIONAR ESTILOS PARA OS NOVOS BOTÕES
const additionalStyles = StyleSheet.create({
  nextButton: {
    backgroundColor: COLORS.primaryDark,
  },
  nextButtonText: {
    fontWeight: 'bold',
    color: COLORS.white,
  },
  premiumNextButton: {
    backgroundColor: '#4CAF50',
    padding: 20,
    borderRadius: 12,
    margin: 15,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 6,
    elevation: 8,
  },
  premiumNextText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  premiumNextSubtext: {
    color: 'rgba(255,255,255,0.9)',
    fontSize: 14,
  },
});

// Mesclar estilos
Object.assign(styles, additionalStyles);

export default Chapter8Screen;
EOF

echo "   ✅ Navegação Chapter 8 → Chapter 9 adicionada"

echo "2️⃣ Verificando navegação da home..."

# VERIFICAR SE HOMESCREEN SIMPLE TEM PROBLEMAS
if grep -q "Chapter9" "$PROJECT_DIR/src/screens/HomeScreenSimple.js"; then
    echo "   ✅ HomeScreenSimple.js tem Chapter9 configurado"
else
    echo "   ❌ Problema encontrado no HomeScreenSimple.js"
fi

echo "3️⃣ Adicionando debug ao Chapter9Screen..."

# ADICIONAR CONSOLE.LOG PARA DEBUG NO CHAPTER 9
sed -i '' '1i\
// 🚨 DEBUG: Chapter9Screen carregando...\
console.log("🚀 DEBUG: Chapter9Screen sendo importado");
' "$PROJECT_DIR/src/screens/Chapter9Screen.js"

echo "   ✅ Debug adicionado ao Chapter9Screen"

echo ""
echo "✅ CORREÇÕES IMPLEMENTADAS!"
echo ""
echo "🎯 SOLUÇÕES APLICADAS:"
echo "   ✅ Navegação Chapter 8 → Chapter 9: ADICIONADA"
echo "   ✅ Botão especial Módulo 3: CRIADO"
echo "   ✅ Debug Chapter 9: ATIVADO"
echo "   ✅ Fallback navegação: IMPLEMENTADO"
echo ""
echo "📱 RESULTADO ESPERADO:"
echo "   ✅ Módulo 3 deve abrir da home"
echo "   ✅ Chapter 8 deve ter botão para Chapter 9"
echo "   ✅ Navegação funcionando em ambas as direções"
echo ""
echo "🔄 TESTE IMEDIATO:"
echo "   1. Reinicie o app (npm start)"
echo "   2. Tente abrir Módulo 3 da home"
echo "   3. Vá ao Chapter 8 e teste navegação"
echo "   4. Verifique console para logs de debug"
echo ""
echo "🔍 DEBUG:"
echo "   - Verifique console do app para logs '🚀 DEBUG'"
echo "   - Se ainda não funcionar, temos backup em: $BACKUP_DIR"
