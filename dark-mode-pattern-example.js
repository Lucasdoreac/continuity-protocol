// 🎯 EXEMPLO PRÁTICO: Padrão dos "Módulos Extras" aplicado
// Demonstrando como implementar fundo escuro + texto claro corretamente

// PADRÃO QUE FUNCIONA (baseado em HomeScreenSimple.js)
const COLORS = useLegacyColors(); // Hook que não quebra

// ESTILOS DINÂMICOS - Seguindo padrão dos "Módulos Extras"
const dynamicStyles = StyleSheet.create({
  // Container principal - como os cards dos módulos extras
  container: {
    backgroundColor: COLORS.cardBackground || COLORS.surface, // Fundo escuro no modo escuro
    borderRadius: 12,
    padding: 20,
    marginVertical: 10,
    borderLeftWidth: 4,
    borderLeftColor: COLORS.accent, // Destaque colorido
    shadowColor: COLORS.shadow || '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  
  // Título - texto claro no modo escuro
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.text, // Dinâmico: branco no escuro, preto no claro
    marginBottom: 15,
  },
  
  // Inputs - adaptáveis ao tema
  input: {
    borderWidth: 1,
    borderColor: COLORS.border || COLORS.lightGray,
    backgroundColor: COLORS.background,
    color: COLORS.text,
    padding: 12,
    borderRadius: 8,
    marginBottom: 10,
    fontSize: 16,
  },
  
  // Botão - seguindo padrão visual dos módulos
  button: {
    backgroundColor: COLORS.primary,
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 10,
  },
  
  buttonText: {
    color: COLORS.white,
    fontWeight: 'bold',
    fontSize: 16,
  },
  
  // Resultado - texto claro e legível
  result: {
    backgroundColor: COLORS.surface,
    padding: 15,
    borderRadius: 8,
    marginTop: 15,
    borderWidth: 1,
    borderColor: COLORS.accent,
  },
  
  resultText: {
    color: COLORS.text, // Dinâmico
    fontSize: 16,
    fontWeight: 'bold',
  }
});

// USO NO COMPONENTE:
return (
  <View style={dynamicStyles.container}>
    <Text style={dynamicStyles.title}>🧮 Calculadora de Juros Compostos</Text>
    
    <TextInput
      style={dynamicStyles.input}
      placeholder="Valor inicial"
      placeholderTextColor={COLORS.textSecondary}
      value={initialValue}
      onChangeText={setInitialValue}
    />
    
    <TouchableOpacity 
      style={dynamicStyles.button}
      onPress={calculate}
    >
      <Text style={dynamicStyles.buttonText}>Calcular</Text>
    </TouchableOpacity>
    
    {result && (
      <View style={dynamicStyles.result}>
        <Text style={dynamicStyles.resultText}>{result}</Text>
      </View>
    )}
  </View>
);
