import React, { useState } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  TextInput, 
  TouchableOpacity 
} from 'react-native';
import { COLORS } from '../styles/globalStyles';
import { useColors } from '../contexts/ThemeContext';

const TaxCalculator = () => {
  
  const [investment, setInvestment] = useState({
    initialAmount: '10000',
    finalAmount: '12000',
    days: '365',
    investmentType: 'rendaFixa', // rendaFixa, fundos, acoes, acoesSwingTrade, acoesDayTrade
    monthlyTradeVolume: '15000' // Para controle do limite de R$20.000/mês
  });
  
  const [results, setResults] = useState(null);
  const [errors, setErrors] = useState([]);

  // Validação de entrada aprimorada
  const validateInputs = () => {
    const newErrors = [];
    const initial = parseFloat(investment.initialAmount);
    const final = parseFloat(investment.finalAmount);
    const days = parseInt(investment.days);
    
    if (!investment.initialAmount || initial <= 0) {
      newErrors.push('Valor inicial deve ser maior que zero');
    }
    
    if (!investment.finalAmount || final <= 0) {
      newErrors.push('Valor final deve ser maior que zero');
    }
    
    if (!investment.days || days <= 0) {
      newErrors.push('Período deve ser maior que zero');
    }
    
    if (initial && final && final < initial) {
      newErrors.push('Valor final deve ser maior que inicial');
    }
    
    setErrors(newErrors);
    return newErrors.length === 0;
  };

  // Cálculo de rentabilidade anualizada
  const calculateAnnualizedReturn = (initial, final, days) => {
    const totalReturn = (final / initial) - 1;
    return Math.pow(1 + totalReturn, 365 / days) - 1;
  };

  // Formatação de percentual aprimorada
  const formatPercentage = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'percent',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  // Dicas de otimização fiscal automáticas
  const getTaxOptimizationTips = (days, type, iofAmount, irRate) => {
    const tips = [];
    
    if (days < 30) {
      tips.push({
        type: 'warning',
        title: '⚠️ IOF Alto!',
        message: `Aguardar mais ${30 - days} dias eliminaria o IOF de ${formatCurrency(iofAmount)}`
      });
    }
    
    if (days > 180 && days < 361 && (type === 'rendaFixa' || type === 'fundos')) {
      tips.push({
        type: 'info',
        title: '📉 IR pode melhorar',
        message: `Aguardando mais ${361 - days} dias, IR cairia de 20% para 17,5%`
      });
    }
    
    if (days > 360 && days < 721 && (type === 'rendaFixa' || type === 'fundos')) {
      tips.push({
        type: 'success',
        title: '🎯 Melhor tributação em vista',
        message: `Em mais ${721 - days} dias, IR seria apenas 15% (menor alíquota)`
      });
    }
    
    return tips;
  };

  // Lógica corrigida de IR baseada no tipo de investimento
  const getIRRate = (days, type, monthlyVolume = 0) => {
    switch (type) {
      case 'acoes':
      case 'acoesSwingTrade':
        // Ações pessoa física - isento até R$20.000/mês de vendas
        if (monthlyVolume <= 20000) return 0;
        return 0.15; // 15% sobre o ganho acima do limite
        
      case 'acoesDayTrade':
        return 0.20; // 20% sempre para day trade
        
      case 'fundos':
        // Fundos seguem tabela regressiva igual renda fixa
        if (days <= 180) return 0.225; // 22,5%
        if (days <= 360) return 0.20;  // 20%
        if (days <= 720) return 0.175; // 17,5%
        return 0.15; // 15%
        
      case 'rendaFixa':
      default:
        // Tabela regressiva padrão para renda fixa
        if (days <= 180) return 0.225; // 22,5%
        if (days <= 360) return 0.20;  // 20%
        if (days <= 720) return 0.175; // 17,5%
        return 0.15; // 15%
    }
  };

  // Tabela IOF oficial (Circular STN 01/2022) - mais legível
  const getIOFRate = (days) => {
    if (days >= 30) return 0;
    
    const iofTable = {
      1: 96, 2: 93, 3: 90, 4: 86, 5: 83, 6: 80, 7: 76, 8: 73, 9: 70, 10: 66,
      11: 63, 12: 60, 13: 56, 14: 53, 15: 50, 16: 46, 17: 43, 18: 40, 19: 36, 20: 33,
      21: 30, 22: 26, 23: 23, 24: 20, 25: 16, 26: 13, 27: 10, 28: 6, 29: 3, 30: 0
    };
    
    return (iofTable[days] || 0) / 100;
  };

  const calculateTaxes = () => {
    // Validar entrada antes de calcular
    if (!validateInputs()) return;

    const initial = parseFloat(investment.initialAmount);
    const final = parseFloat(investment.finalAmount);
    const days = parseInt(investment.days);
    const monthlyVolume = parseFloat(investment.monthlyTradeVolume) || 0;
    const profit = final - initial;
    
    if (profit <= 0) {
      setResults({
        profit: 0,
        irRate: 0,
        iofRate: 0,
        irAmount: 0,
        iofAmount: 0,
        totalTaxes: 0,
        netAmount: final,
        netProfit: profit,
        isExempt: false,
        exemptReason: '',
        annualizedReturn: 0,
        effectiveReturn: 0,
        tips: []
      });
      return;
    }
    
    const irRate = getIRRate(days, investment.investmentType, monthlyVolume);
    const iofRate = getIOFRate(days);
    
    // Verificar se está isento
    const isExempt = irRate === 0;
    let exemptReason = '';
    
    if (isExempt && (investment.investmentType === 'acoes' || investment.investmentType === 'acoesSwingTrade')) {
      exemptReason = 'Ações pessoa física - vendas até R$20.000/mês são isentas de IR';
    }
    
    const irAmount = profit * irRate;
    const iofAmount = profit * iofRate;
    const totalTaxes = irAmount + iofAmount;
    
    const netAmount = final - totalTaxes;
    const netProfit = profit - totalTaxes;
    
    // Calcular rentabilidades
    const annualizedReturn = calculateAnnualizedReturn(initial, final, days);
    const effectiveReturn = netProfit / initial;
    
    // Gerar dicas de otimização
    const tips = getTaxOptimizationTips(days, investment.investmentType, iofAmount, irRate);
    
    setResults({
      profit,
      irRate: irRate * 100,
      iofRate: iofRate * 100,
      irAmount,
      iofAmount,
      totalTaxes,
      netAmount,
      netProfit,
      days,
      isExempt,
      exemptReason,
      monthlyVolume,
      annualizedReturn,
      effectiveReturn,
      tips
    });
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const InvestmentTypeButton = ({ type, label, isSelected, onPress }) => (
    <TouchableOpacity
      style={[
        styles.typeButton,
        isSelected && styles.typeButtonSelected
      ]}
      onPress={onPress}
    >
      <Text style={[
        styles.typeButtonText,
        isSelected && styles.typeButtonTextSelected
      ]}>
        {label}
      </Text>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.title}>🧾 Calculadora de Impostos Aprimorada</Text>
      
      {/* Exibir erros de validação */}
      {errors.length > 0 && (
        <View style={styles.errorContainer}>
          {errors.map((error, index) => (
            <Text key={index} style={styles.errorText}>⚠️ {error}</Text>
          ))}
        </View>
      )}
      
      {/* REMOVIDO ScrollView - agora usa View normal para evitar nested scroll */}
      <View style={styles.contentContainer}>
        <View style={styles.inputSection}>
          <Text style={styles.sectionTitle}>Tipo de Investimento</Text>
          <View style={styles.typeContainer}>
            <InvestmentTypeButton
              type="rendaFixa"
              label="Renda Fixa"
              isSelected={investment.investmentType === 'rendaFixa'}
              onPress={() => setInvestment({...investment, investmentType: 'rendaFixa'})}
            />
            <InvestmentTypeButton
              type="fundos"
              label="Fundos"
              isSelected={investment.investmentType === 'fundos'}
              onPress={() => setInvestment({...investment, investmentType: 'fundos'})}
            />
          </View>
          <View style={[styles.typeContainer, {marginTop: 8}]}>
            <InvestmentTypeButton
              type="acoes"
              label="Ações PF"
              isSelected={investment.investmentType === 'acoes'}
              onPress={() => setInvestment({...investment, investmentType: 'acoes'})}
            />
            <InvestmentTypeButton
              type="acoesSwingTrade"
              label="Swing Trade"
              isSelected={investment.investmentType === 'acoesSwingTrade'}
              onPress={() => setInvestment({...investment, investmentType: 'acoesSwingTrade'})}
            />
            <InvestmentTypeButton
              type="acoesDayTrade"
              label="Day Trade"
              isSelected={investment.investmentType === 'acoesDayTrade'}
              onPress={() => setInvestment({...investment, investmentType: 'acoesDayTrade'})}
            />
          </View>
        </View>
        
        <View style={styles.inputCard}>
          <View style={styles.inputContainer}>
            <Text style={styles.inputLabel}>Valor Inicial Investido (R$)</Text>
            <TextInput
              style={styles.input}
              value={investment.initialAmount}
              onChangeText={(text) => setInvestment({...investment, initialAmount: text})}
              keyboardType="numeric"
              placeholder="10000"
              placeholderTextColor="#999"
            />
          </View>
          
          <View style={styles.inputContainer}>
            <Text style={styles.inputLabel}>Valor Final do Investimento (R$)</Text>
            <TextInput
              style={styles.input}
              value={investment.finalAmount}
              onChangeText={(text) => setInvestment({...investment, finalAmount: text})}
              keyboardType="numeric"
              placeholder="12000"
              placeholderTextColor="#999"
            />
          </View>
          
          <View style={styles.inputContainer}>
            <Text style={styles.inputLabel}>Período do Investimento (dias)</Text>
            <TextInput
              style={styles.input}
              value={investment.days}
              onChangeText={(text) => setInvestment({...investment, days: text})}
              keyboardType="numeric"
              placeholder="365"
              placeholderTextColor="#999"
            />
          </View>
          
          {/* Campo de volume mensal apenas para ações */}
          {(investment.investmentType === 'acoes' || investment.investmentType === 'acoesSwingTrade') && (
            <View style={styles.inputContainer}>
              <Text style={styles.inputLabel}>Volume Mensal de Vendas (R$)</Text>
              <Text style={styles.inputHelper}>Para ações pessoa física (limite R$20.000/mês)</Text>
              <TextInput
                style={styles.input}
                value={investment.monthlyTradeVolume}
                onChangeText={(text) => setInvestment({...investment, monthlyTradeVolume: text})}
                keyboardType="numeric"
                placeholder="15000"
                placeholderTextColor="#999"
              />
            </View>
          )}
        </View>
        
        <TouchableOpacity style={styles.calculateButton} onPress={calculateTaxes}>
          <Text style={styles.calculateButtonText}>Calcular Impostos</Text>
        </TouchableOpacity>
        
        {results && (
          <View style={styles.resultsContainer}>
            <Text style={styles.resultsTitle}>📊 Resultado da Tributação</Text>
            
            <View style={styles.profitCard}>
              <Text style={styles.profitAmount}>
                {formatCurrency(results.profit)}
              </Text>
              <Text style={styles.profitLabel}>Lucro Bruto</Text>
              {/* Rentabilidade anualizada */}
              <Text style={styles.returnInfo}>
                Rentabilidade: {formatPercentage(results.effectiveReturn)} • 
                Anualizada: {formatPercentage(results.annualizedReturn)}
              </Text>
            </View>
            
            <View style={styles.taxBreakdown}>
              <View style={styles.taxRow}>
                <Text style={styles.taxLabel}>💰 Imposto de Renda ({results.irRate.toFixed(1)}%)</Text>
                <Text style={styles.taxAmount}>{formatCurrency(results.irAmount)}</Text>
              </View>
              
              <View style={styles.taxRow}>
                <Text style={styles.taxLabel}>⏱️ IOF ({results.iofRate.toFixed(1)}%)</Text>
                <Text style={styles.taxAmount}>{formatCurrency(results.iofAmount)}</Text>
              </View>
              
              <View style={[styles.taxRow, styles.totalTaxRow]}>
                <Text style={styles.totalTaxLabel}>Total de Impostos</Text>
                <Text style={styles.totalTaxAmount}>{formatCurrency(results.totalTaxes)}</Text>
              </View>
            </View>
            
            <View style={styles.finalResults}>
              <View style={styles.finalCard}>
                <Text style={styles.finalAmount}>{formatCurrency(results.netAmount)}</Text>
                <Text style={styles.finalLabel}>Valor Líquido Final</Text>
              </View>
              
              <View style={styles.finalCard}>
                <Text style={styles.finalProfit}>{formatCurrency(results.netProfit)}</Text>
                <Text style={styles.finalLabel}>Lucro Líquido</Text>
              </View>
            </View>
            
            {/* Informações sobre isenção quando aplicável */}
            {results.isExempt && (
              <View style={styles.exemptBox}>
                <Text style={styles.exemptTitle}>✅ Investimento Isento de IR</Text>
                <Text style={styles.exemptText}>{results.exemptReason}</Text>
              </View>
            )}
            
            <View style={styles.infoBox}>
              <Text style={styles.infoTitle}>📅 Informações sobre o Prazo</Text>
              {results.days <= 30 && (
                <Text style={styles.infoText}>
                  ⚠️ <Text style={styles.highlight}>IOF aplicável!</Text> Investimentos com prazo inferior a 30 dias são tributados pelo IOF regressivo.
                </Text>
              )}
              {results.days > 30 && results.days <= 180 && (
                <Text style={styles.infoText}>
                  📈 <Text style={styles.highlight}>IR de 22,5%</Text> aplicável para investimentos de até 180 dias.
                </Text>
              )}
              {results.days > 180 && results.days <= 720 && (
                <Text style={styles.infoText}>
                  📉 <Text style={styles.highlight}>IR regressivo</Text> - quanto maior o prazo, menor a alíquota!
                </Text>
              )}
              {results.days > 720 && (
                <Text style={styles.infoText}>
                  🎯 <Text style={styles.highlight}>Menor alíquota (15%)</Text> para investimentos acima de 2 anos!
                </Text>
              )}
              {investment.investmentType === 'acoesDayTrade' && (
                <Text style={styles.infoText}>
                  ⚡ <Text style={styles.highlight}>Day Trade (20% IR)</Text> - Tributação fixa independente do prazo!
                </Text>
              )}
              {(investment.investmentType === 'acoes' || investment.investmentType === 'acoesSwingTrade') && results.monthlyVolume <= 20000 && (
                <Text style={styles.infoText}>
                  💰 <Text style={styles.highlight}>Ações PF Isentas</Text> - Vendas até R$20.000/mês são isentas de IR!
                </Text>
              )}
              {(investment.investmentType === 'acoes' || investment.investmentType === 'acoesSwingTrade') && results.monthlyVolume > 20000 && (
                <Text style={styles.infoText}>
                  📊 <Text style={styles.highlight}>IR de 15%</Text> sobre ganhos acima do limite mensal de R$20.000.
                </Text>
              )}
              {investment.investmentType === 'fundos' && (
                <Text style={styles.infoText}>
                  📈 <Text style={styles.highlight}>Fundos</Text> seguem tabela regressiva igual renda fixa.
                </Text>
              )}
            </View>
          </View>
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#f9f9f9',
    borderRadius: 8,
    padding: 15,
    marginVertical: 15,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.primaryDark,
    marginBottom: 15,
    textAlign: 'center',
  },
  contentContainer: {
    // Removido maxHeight - agora usa altura natural
  },
  inputSection: {
    marginBottom: 15,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: COLORS.primaryDark,
    marginBottom: 10,
  },
  typeContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  typeButton: {
    flex: 1,
    backgroundColor: 'white',
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 5,
    padding: 8,
    alignItems: 'center',
    marginHorizontal: 2,
  },
  typeButtonSelected: {
    backgroundColor: COLORS.primaryDark,
    borderColor: COLORS.primaryDark,
  },
  typeButtonText: {
    fontSize: 11,
    color: '#666',
    fontWeight: '500',
    textAlign: 'center',
  },
  typeButtonTextSelected: {
    color: 'white',
    fontWeight: 'bold',
  },
  inputCard: {
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 15,
    marginBottom: 15,
  },
  inputContainer: {
    marginBottom: 12,
  },
  inputLabel: {
    fontSize: 14,
    color: '#333',
    marginBottom: 5,
    fontWeight: '500',
  },
  inputHelper: {
    fontSize: 12,
    color: '#666',
    marginBottom: 5,
    fontStyle: 'italic',
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 5,
    padding: 10,
    fontSize: 16,
    backgroundColor: 'white',
  },
  calculateButton: {
    backgroundColor: COLORS.primaryDark,
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 15,
  },
  calculateButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  resultsContainer: {
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 15,
  },
  resultsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.primaryDark,
    marginBottom: 15,
    textAlign: 'center',
  },
  profitCard: {
    backgroundColor: COLORS.primaryLight,
    borderRadius: 8,
    padding: 15,
    alignItems: 'center',
    marginBottom: 15,
  },
  profitAmount: {
    fontSize: 24,
    fontWeight: 'bold',
    color: COLORS.primaryDark,
  },
  profitLabel: {
    fontSize: 14,
    color: '#666',
    marginTop: 5,
  },
  taxBreakdown: {
    marginBottom: 15,
  },
  taxRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  totalTaxRow: {
    borderBottomWidth: 2,
    borderBottomColor: COLORS.primaryDark,
    marginTop: 5,
  },
  taxLabel: {
    fontSize: 14,
    color: '#333',
  },
  taxAmount: {
    fontSize: 14,
    fontWeight: '600',
    color: '#e74c3c',
  },
  totalTaxLabel: {
    fontSize: 16,
    fontWeight: 'bold',
    color: COLORS.primaryDark,
  },
  totalTaxAmount: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#e74c3c',
  },
  finalResults: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 15,
  },
  finalCard: {
    flex: 1,
    backgroundColor: '#f9f9f9',
    borderRadius: 8,
    padding: 12,
    alignItems: 'center',
    marginHorizontal: 5,
  },
  finalAmount: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2c3e50',
  },
  finalProfit: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#27ae60',
  },
  finalLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 5,
  },
  infoBox: {
    backgroundColor: COLORS.primaryLight,
    borderRadius: 8,
    padding: 15,
  },
  infoTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: COLORS.primaryDark,
    marginBottom: 8,
  },
  infoText: {
    fontSize: 13,
    lineHeight: 18,
  },
  highlight: {
    fontWeight: 'bold',
    color: COLORS.primaryDark,
  },
  exemptBox: {
    backgroundColor: '#E8F5E8',
    borderRadius: 8,
    padding: 15,
    marginBottom: 15,
    borderLeftWidth: 4,
    borderLeftColor: '#27ae60',
  },
  exemptTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#27ae60',
    marginBottom: 8,
  },
  exemptText: {
    fontSize: 14,
    color: '#2d5a3d',
    lineHeight: 18,
  },
});

export default TaxCalculator;