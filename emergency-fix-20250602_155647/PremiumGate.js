import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { useFreemium } from '../contexts/FreemiumContext';
import { COLORS } from '../styles/globalStyles';
import AnalyticsService from '../services/AnalyticsService';

const PremiumGate = ({ 
  children, 
  chapterName, 
  featureName, 
  source = 'chapter_access',
  fallbackContent = null 
}) => {
  const { 
    isPremiumUser, 
    isChapterAccessible, 
    isFeatureAccessible, 
    showUpgradePrompt,
    shouldShowUpgradePrompt,
    markUpgradePromptShown
  } = useFreemium();

  // Verificar se conteúdo é acessível
  const isAccessible = chapterName 
    ? isChapterAccessible(chapterName)
    : featureName 
    ? isFeatureAccessible(featureName)
    : true;

  // Se conteúdo é acessível, renderizar normalmente
  if (isAccessible) {
    return children;
  }

  // Renderizar tela de upgrade para conteúdo premium
  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.contentContainer}>
      {/* Header Premium */}
      <View style={styles.premiumHeader}>
        <Text style={styles.premiumIcon}>🔓</Text>
        <Text style={styles.premiumTitle}>Conteúdo Premium</Text>
        <Text style={styles.premiumSubtitle}>
          {getContentDescription(chapterName, featureName)}
        </Text>
      </View>

      {/* Demonstração do que já é acessível */}
      <View style={styles.demoSection}>
        <Text style={styles.demoTitle}>✅ Você já experimentou:</Text>
        <View style={styles.demoItems}>
          <Text style={styles.demoItem}>📚 Capítulo 1: Importância de Investir aos Poucos</Text>
          <Text style={styles.demoItem}>📊 Calculadora de Juros Compostos</Text>
          <Text style={styles.demoItemHighlight}>🔥 Taxas Reais do Banco Central (EXCLUSIVO!)</Text>
        </View>
      </View>

      {/* Benefícios do Premium */}
      <View style={styles.benefitsSection}>
        <Text style={styles.benefitsTitle}>🚀 Desbloqueie todo o poder:</Text>
        <View style={styles.benefitsList}>
          <Text style={styles.benefit}>📖 Todos os capítulos da Luciana Araújo</Text>
          <Text style={styles.benefit}>🎯 Quiz completo de perfil do investidor</Text>
          <Text style={styles.benefit}>💰 Comparações detalhadas Renda Fixa vs Variável</Text>
          <Text style={styles.benefit}>🛠️ Ferramentas avançadas: metas + carteira</Text>
          <Text style={styles.benefit}>♾️ Simulações ilimitadas com todas as taxas</Text>
          <Text style={styles.benefit}>📱 Exportação de relatórios</Text>
          <Text style={styles.benefit}>💎 20 Dicas Práticas exclusivas</Text>
        </View>
      </View>

      {/* Botões de ação */}
      <View style={styles.actionButtons}>
        <TouchableOpacity 
          style={styles.upgradeButton}
          onPress={() => handleUpgradePress(chapterName, featureName, source)}
        >
          <Text style={styles.upgradeButtonText}>🚀 Desbloquear Agora</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.backButton}
          onPress={() => handleBackPress(chapterName, featureName, source)}
        >
          <Text style={styles.backButtonText}>← Voltar ao Capítulo 1</Text>
        </TouchableOpacity>
      </View>

      {/* Preço e valor */}
      <View style={styles.priceSection}>
        <Text style={styles.priceText}>
          💡 Investimento único para educação financeira completa
        </Text>
        <Text style={styles.valueText}>
          Menos que o preço de um café por dia! ☕
        </Text>
      </View>

      {/* Fallback content se fornecido */}
      {fallbackContent && (
        <View style={styles.fallbackSection}>
          {fallbackContent}
        </View>
      )}
    </ScrollView>
  );

  // Funções auxiliares
  function getContentDescription(chapterName, featureName) {
    const descriptions = {
      'Chapter2': 'Aprenda sobre o Triângulo Impossível dos investimentos',
      'Chapter3': 'Descubra seu perfil de investidor completo',
      'Chapter4': 'Domine Renda Fixa com comparações detalhadas',
      'Chapter5': 'Explore Renda Variável com estratégias práticas',
      'Chapter6': 'Acesse as 20 Dicas Práticas da Luciana',
      'Chapter7': 'Módulo Impostos e Tributação',
      'Chapter8': 'Módulo Estratégias Práticas',
      'Chapter9': 'Módulo Ferramentas Avançadas',
      'advanced_tools': 'Ferramentas de metas e carteira',
      'unlimited_simulations': 'Simulações ilimitadas',
      'default': 'Continue sua jornada de educação financeira'
    };
    
    const key = chapterName || featureName || 'default';
    return descriptions[key] || descriptions.default;
  }

  async function handleUpgradePress(chapterName, featureName, source) {
    const targetFeature = chapterName || featureName || 'premium_access';
    
    // 📊 ANALYTICS: Premium feature visualizada
    await AnalyticsService.logEvent(AnalyticsService.EVENTS.PREMIUM_FEATURE_VIEWED, {
      feature_name: targetFeature,
      source_screen: source,
      user_type: 'freemium'
    });

    // Verificar se deve mostrar prompt (anti-spam)
    const shouldShow = await shouldShowUpgradePrompt(targetFeature);
    if (shouldShow) {
      await markUpgradePromptShown(targetFeature);
      await showUpgradePrompt(targetFeature, source);
    }
  }

  async function handleBackPress(chapterName, featureName, source) {
    // 📊 ANALYTICS: Usuário voltou sem converter
    await AnalyticsService.logEvent('premium_gate_back_pressed', {
      blocked_feature: chapterName || featureName,
      source_screen: source,
      user_type: 'freemium'
    });

    // TODO: Implementar navegação de volta programática se necessário
    // Por enquanto, usuário usará botão nativo do header
  }
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  contentContainer: {
    padding: 20,
  },
  premiumHeader: {
    alignItems: 'center',
    marginBottom: 30,
    paddingVertical: 20,
    backgroundColor: COLORS.primary,
    borderRadius: 15,
  },
  premiumIcon: {
    fontSize: 50,
    marginBottom: 10,
  },
  premiumTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: COLORS.white,
    marginBottom: 8,
  },
  premiumSubtitle: {
    fontSize: 16,
    color: COLORS.white,
    textAlign: 'center',
    opacity: 0.9,
    paddingHorizontal: 20,
  },
  demoSection: {
    backgroundColor: COLORS.success + '20',
    padding: 15,
    borderRadius: 10,
    marginBottom: 20,
    borderLeftWidth: 4,
    borderLeftColor: COLORS.success,
  },
  demoTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: COLORS.success,
    marginBottom: 10,
  },
  demoItems: {
    paddingLeft: 10,
  },
  demoItem: {
    fontSize: 14,
    color: COLORS.text,
    marginBottom: 5,
  },
  demoItemHighlight: {
    fontSize: 14,
    color: COLORS.accent,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  benefitsSection: {
    backgroundColor: COLORS.white,
    padding: 15,
    borderRadius: 10,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  benefitsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.primary,
    marginBottom: 15,
  },
  benefitsList: {
    paddingLeft: 10,
  },
  benefit: {
    fontSize: 15,
    color: COLORS.text,
    marginBottom: 8,
    lineHeight: 22,
  },
  actionButtons: {
    marginBottom: 20,
  },
  upgradeButton: {
    backgroundColor: COLORS.accent,
    paddingVertical: 16,
    paddingHorizontal: 30,
    borderRadius: 25,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 5,
  },
  upgradeButtonText: {
    color: COLORS.white,
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  backButton: {
    backgroundColor: COLORS.gray + '40',
    paddingVertical: 12,
    paddingHorizontal: 30,
    borderRadius: 20,
  },
  backButtonText: {
    color: COLORS.text,
    fontSize: 16,
    textAlign: 'center',
  },
  priceSection: {
    alignItems: 'center',
    marginBottom: 20,
    paddingVertical: 15,
  },
  priceText: {
    fontSize: 14,
    color: COLORS.text,
    textAlign: 'center',
    marginBottom: 5,
  },
  valueText: {
    fontSize: 12,
    color: COLORS.gray,
    textAlign: 'center',
    fontStyle: 'italic',
  },
  fallbackSection: {
    marginTop: 20,
    padding: 15,
    backgroundColor: COLORS.gray + '20',
    borderRadius: 10,
  },
});

export default PremiumGate;
