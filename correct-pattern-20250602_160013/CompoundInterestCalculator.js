import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  TextInput, 
  StyleSheet, 
  TouchableOpacity,
  Platform,
  Alert
} from 'react-native';
import { COLORS, globalStyles } from '../styles/globalStyles';
import RatesService from '../services/RatesService';
import AnalyticsService from '../services/AnalyticsService';
import { useGamification } from '../contexts/GamificationContext';

const CompoundInterestCalculator = () => {
  
  // Hook de gamificação
  const { recordCalculationPerformed, recordTaxasReaisUsed } = useGamification();
  
  // Estados para controlar os inputs e resultados
  const [initialValue, setInitialValue] = useState('0');
  const [monthlyValue, setMonthlyValue] = useState('100');
  const [interestRate, setInterestRate] = useState('0.8');
  const [period, setPeriod] = useState('10');
  const [result, setResult] = useState(null);
  const [totalInvested, setTotalInvested] = useState(0);
  const [interestEarned, setInterestEarned] = useState(0);

  // Usar taxa real - DIFERENCIAL ÚNICO DO APP
  const useRealRate = async (rateType) => {
    try {
      // 📊 ANALYTICS: Evento principal - taxas reais clicked
      await AnalyticsService.logTaxasReaisClicked('CompoundInterest', 'Chapter1');
      
      // 🎮 GAMIFICAÇÃO: Registrar uso de taxas reais (diferencial único)
      await recordTaxasReaisUsed('CompoundInterest');
      
      Alert.alert('⏳ Carregando...', 'Buscando taxa oficial atual...');
      
      const ratesData = await RatesService.getAllRates();
      
      if (ratesData.rates && ratesData.rates[rateType]) {
        const yearlyRate = ratesData.rates[rateType].value;
        // Converter taxa anual para mensal
        const monthlyRate = (Math.pow(1 + yearlyRate/100, 1/12) - 1) * 100;
        
        setInterestRate(monthlyRate.toFixed(3));
        
        const rateLabels = {
          selic: 'Taxa Selic (juros básicos)',
          cdi: 'Taxa CDI (CDB, LCI, LCA)', 
          poupanca: 'Poupança (caderneta)'
        };
        
        const rateLabel = rateLabels[rateType];
        
        Alert.alert(
          '✅ Taxa Oficial Aplicada!',
          `${rateLabel}\n\n` +
          `📊 Taxa anual: ${yearlyRate.toFixed(2)}% a.a.\n` +
          `🗓️ Taxa mensal: ${monthlyRate.toFixed(3)}% a.m.\n\n` +
          `${ratesData.isStale ? '⚠️ Dados offline (última atualização)' : '🌐 Dados atualizados'}\n\n` +
          `Agora você pode calcular com a taxa oficial!`,
          [{ text: 'Entendi', style: 'default' }]
        );
      } else {
        throw new Error('Taxa não disponível');
      }
    } catch (error) {
      console.log('Erro ao buscar taxa:', error);
      Alert.alert(
        '❌ Erro de Conexão',
        'Não foi possível carregar a taxa oficial atual.\n\n' +
        'Verifique sua conexão com a internet e tente novamente.',
        [{ text: 'OK', style: 'default' }]
      );
    }
  };

  // Calcula o resultado dos juros compostos
  const calculateCompoundInterest = async () => {
    const initial = parseFloat(initialValue) || 0;
    const monthly = parseFloat(monthlyValue) || 0;
    const rate = (parseFloat(interestRate) || 0) / 100;
    const years = parseFloat(period) || 0;
    
    // 📊 ANALYTICS: Calculator usado
    await AnalyticsService.logCalculatorUsed(
      'CompoundInterest', 
      'juros_compostos',
      initial + (monthly * years * 12) // Total que será investido
    );
    
    // 🎮 GAMIFICAÇÃO: Registrar simulação realizada
    await recordCalculationPerformed('CompoundInterest');
    
    let futureValue = initial;
    let invested = initial;
    
    // Cálculo mensal ao longo dos anos
    for (let i = 0; i < years * 12; i++) {
      futureValue = futureValue * (1 + rate) + monthly;
      invested += monthly;
    }
    
    // Arredonda para 2 casas decimais
    futureValue = Math.round(futureValue * 100) / 100;
    invested = Math.round(invested * 100) / 100;
    
    setResult(futureValue);
    setTotalInvested(invested);
    setInterestEarned(futureValue - invested);
    
    // 📊 ANALYTICS: Simulação completada
    await AnalyticsService.logEvent(AnalyticsService.EVENTS.SIMULATION_COMPLETED, {
      calculator_type: 'CompoundInterest',
      initial_value: initial,
      monthly_value: monthly,
      interest_rate: rate * 100,
      period_years: years,
      final_result: futureValue,
      interest_earned: futureValue - invested
    });
  };

  // Calcula o resultado sempre que os valores mudarem
  useEffect(() => {
    calculateCompoundInterest();
  }, [initialValue, monthlyValue, interestRate, period]);

  // Formata para exibição com R$ e pontuação
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  };

  return (
    <View style={styles.container}>
      <View style={styles.card}>
          <Text style={styles.title}>💰 Calculadora de Juros Compostos</Text>
          <Text style={styles.description}>
            Descubra como pequenos investimentos mensais podem se transformar em um patrimônio significativo ao longo do tempo.
          </Text>
          
          <View style={styles.inputContainer}>
            <Text style={styles.label}>Valor inicial (R$):</Text>
            <TextInput
              style={styles.input}
              value={initialValue}
              onChangeText={setInitialValue}
              keyboardType="numeric"
              placeholder="Ex: 500"
            />
          </View>
          
          <View style={styles.inputContainer}>
            <Text style={styles.label}>Investimento mensal (R$):</Text>
            <TextInput
              style={styles.input}
              value={monthlyValue}
              onChangeText={setMonthlyValue}
              keyboardType="numeric"
              placeholder="Ex: 100"
            />
          </View>
          
          <View style={styles.inputContainer}>
            <Text style={styles.label}>Taxa de juros mensal (%):</Text>
            <TextInput
              style={styles.input}
              value={interestRate}
              onChangeText={setInterestRate}
              keyboardType="numeric"
              placeholder="Ex: 0.8"
            />
            
            {/* Botões de Taxas Reais */}
            <View style={styles.realRatesButtons}>
              <Text style={styles.realRatesTitle}>📊 Usar taxas oficiais atuais:</Text>
              
              <TouchableOpacity 
                style={styles.realRateButton}
                onPress={() => useRealRate('selic')}
              >
                <Text style={styles.realRateButtonText}>💰 Taxa Selic</Text>
                <Text style={styles.realRateButtonSubtext}>Taxa básica de juros</Text>
              </TouchableOpacity>
              
              <TouchableOpacity 
                style={styles.realRateButton}
                onPress={() => useRealRate('cdi')}
              >
                <Text style={styles.realRateButtonText}>🏦 Taxa CDI</Text>
                <Text style={styles.realRateButtonSubtext}>CDB, LCI, LCA</Text>
              </TouchableOpacity>
              
              <TouchableOpacity 
                style={styles.realRateButton}
                onPress={() => useRealRate('poupanca')}
              >
                <Text style={styles.realRateButtonText}>🐷 Poupança</Text>
                <Text style={styles.realRateButtonSubtext}>Caderneta tradicional</Text>
              </TouchableOpacity>
            </View>
          </View>
          
          <View style={styles.inputContainer}>
            <Text style={styles.label}>Período (anos):</Text>
            <TextInput
              style={styles.input}
              value={period}
              onChangeText={setPeriod}
              keyboardType="numeric"
              placeholder="Ex: 10"
            />
          </View>
          
          <TouchableOpacity 
            style={styles.calculateButton}
            onPress={calculateCompoundInterest}
          >
            <Text style={styles.calculateButtonText}>Calcular</Text>
          </TouchableOpacity>
          
          {result !== null && (
            <View style={styles.resultContainer}>
              <Text style={styles.resultTitle}>Resultados após {period} anos:</Text>
              
              <View style={styles.resultItem}>
                <Text style={styles.resultLabel}>Total acumulado:</Text>
                <Text style={styles.resultValue}>{formatCurrency(result)}</Text>
              </View>
              
              <View style={styles.resultItem}>
                <Text style={styles.resultLabel}>Total investido:</Text>
                <Text style={styles.resultValue}>{formatCurrency(totalInvested)}</Text>
              </View>
              
              <View style={styles.resultItem}>
                <Text style={styles.resultLabel}>Juros ganhos:</Text>
                <Text style={[styles.resultValue, styles.highlight]}>
                  {formatCurrency(interestEarned)}
                </Text>
              </View>
              
              <Text style={styles.tip}>
                <Text style={styles.tipHighlight}>💡 Dica:</Text> Lembre-se que a consistência é mais importante que o valor inicial. Comece com o quanto puder, mesmo que seja R$30 por mês.
              </Text>
            </View>
          )}
        </View>
      </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: COLORS.white,
  },
  card: {
    backgroundColor: COLORS.white,
    borderRadius: 8,
    padding: 15,
    margin: 15,
    shadowColor: COLORS.black,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: COLORS.primaryDark,
    marginBottom: 10,
    textAlign: 'center',
  },
  description: {
    fontSize: 16,
    color: COLORS.black,
    marginBottom: 20,
    textAlign: 'center',
    lineHeight: 22,
  },
  inputContainer: {
    marginBottom: 15,
  },
  label: {
    fontSize: 16,
    color: COLORS.primaryDark,
    marginBottom: 5,
  },
  input: {
    borderWidth: 1,
    borderColor: COLORS.primaryLight,
    borderRadius: 5,
    padding: 10,
    fontSize: 16,
    backgroundColor: '#fafafa',
  },
  calculateButton: {
    backgroundColor: COLORS.primaryDark,
    padding: 15,
    borderRadius: 5,
    alignItems: 'center',
    marginTop: 10,
  },
  calculateButtonText: {
    color: COLORS.white,
    fontWeight: 'bold',
    fontSize: 16,
  },
  resultContainer: {
    marginTop: 20,
    padding: 15,
    backgroundColor: COLORS.primaryLight,
    borderRadius: 8,
  },
  resultTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.primaryDark,
    marginBottom: 15,
    textAlign: 'center',
  },
  resultItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  resultLabel: {
    fontSize: 16,
    color: COLORS.primaryDark,
  },
  resultValue: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  highlight: {
    color: COLORS.primaryDark,
  },
  tip: {
    marginTop: 15,
    fontSize: 14,
    lineHeight: 20,
    color: COLORS.primaryDark,
  },
  tipHighlight: {
    fontWeight: 'bold',
  },
  realRatesButtons: {
    marginTop: 12,
    padding: 16,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#e9ecef',
  },
  realRatesTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: COLORS.primaryDark,
    marginBottom: 12,
    textAlign: 'center',
  },
  realRateButton: {
    backgroundColor: '#2c3e50', // Azul escuro para garantir contraste
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 8,
    borderWidth: 2,
    borderColor: '#34495e',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 3,
    elevation: 3,
  },
  realRateButtonText: {
    color: '#ffffff',  // Branco em fundo escuro - contraste garantido
    fontSize: 14,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 2,
  },
  realRateButtonSubtext: {
    color: '#ecf0f1',  // Cinza bem claro em fundo escuro
    fontSize: 11,
    textAlign: 'center',
  },
});

export default CompoundInterestCalculator;
