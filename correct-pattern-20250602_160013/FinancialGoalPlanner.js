import React, { useState } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  TextInput, 
  TouchableOpacity,
  Alert 
} from 'react-native';
import { COLORS } from '../styles/globalStyles';
import { useSafeColors } from '../contexts/SafeColorsHook';

const FinancialGoalPlanner = () => {
  const colors = useSafeColors(); // 🔧 CORREÇÃO: Hook seguro que nunca quebra
  
  const [goal, setGoal] = useState({
    name: 'Reserva de Emergência',
    targetAmount: '30000',
    currentAmount: '5000',
    monthsToGoal: '24',
    expectedReturn: '12.0'
  });
  
  const [results, setResults] = useState(null);

  const calculateGoal = () => {
    const target = parseFloat(goal.targetAmount);
    const current = parseFloat(goal.currentAmount);
    const months = parseInt(goal.monthsToGoal);
    const monthlyReturn = parseFloat(goal.expectedReturn) / 100 / 12;
    
    if (target <= current) {
      Alert.alert('Atenção', 'O valor atual já atingiu ou superou a meta!');
      return;
    }
    
    const remaining = target - current;
    
    // Calculando valor necessário por mês com juros compostos
    // FV = PMT * [((1 + r)^n - 1) / r] + PV * (1 + r)^n
    // Resolvendo para PMT: PMT = (FV - PV * (1 + r)^n) / [((1 + r)^n - 1) / r]
    
    const futureValueOfCurrent = current * Math.pow(1 + monthlyReturn, months);
    const adjustedTarget = target - futureValueOfCurrent;
    
    let monthlyInvestment;
    if (monthlyReturn === 0) {
      monthlyInvestment = adjustedTarget / months;
    } else {
      const compoundFactor = (Math.pow(1 + monthlyReturn, months) - 1) / monthlyReturn;
      monthlyInvestment = adjustedTarget / compoundFactor;
    }
    
    // Calculando cenários alternativos
    const scenarios = [
      { months: months - 6, label: '6 meses antes' },
      { months: months, label: 'Meta original' },
      { months: months + 6, label: '6 meses depois' },
      { months: months + 12, label: '1 ano depois' }
    ].filter(s => s.months > 0).map(scenario => {
      const futureValue = current * Math.pow(1 + monthlyReturn, scenario.months);
      const adjustedTarget = target - futureValue;
      
      let payment;
      if (monthlyReturn === 0) {
        payment = adjustedTarget / scenario.months;
      } else {
        const compoundFactor = (Math.pow(1 + monthlyReturn, scenario.months) - 1) / monthlyReturn;
        payment = adjustedTarget / compoundFactor;
      }
      
      return {
        ...scenario,
        monthlyPayment: Math.max(0, payment),
        totalInvested: Math.max(0, payment) * scenario.months + current
      };
    });
    
    setResults({
      monthlyInvestment: Math.max(0, monthlyInvestment),
      totalInvested: Math.max(0, monthlyInvestment) * months + current,
      futureValueOfCurrent,
      scenarios,
      goalDetails: goal
    });
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const GoalPreset = ({ name, amount, onSelect }) => (
    <TouchableOpacity
      style={styles.presetButton}
      onPress={() => onSelect(name, amount)}
    >
      <Text style={styles.presetName}>{name}</Text>
      <Text style={styles.presetAmount}>{formatCurrency(amount)}</Text>
    </TouchableOpacity>
  );

  const selectPreset = (name, amount) => {
    setGoal({
      ...goal,
      name,
      targetAmount: amount.toString()
    });
  };

  const presets = [
    { name: 'Reserva de Emergência', amount: 30000 },
    { name: 'Carro Usado', amount: 50000 },
    { name: 'Viagem Internacional', amount: 15000 },
    { name: 'Casa Própria (Entrada)', amount: 80000 },
    { name: 'Aposentadoria', amount: 500000 }
  ];

  return (
    <View style={styles.container}>
      <Text style={styles.title}>🎯 Planejador de Objetivos</Text>
      
      <View style={styles.scrollContainer}>
        <Text style={styles.sectionTitle}>Objetivos Comuns</Text>
        <View style={styles.presetsContainer}>
          {presets.map((preset, index) => (
            <GoalPreset
              key={index}
              name={preset.name}
              amount={preset.amount}
              onSelect={selectPreset}
            />
          ))}
        </View>
        
        <View style={styles.inputCard}>
          <Text style={styles.sectionTitle}>Seu Objetivo</Text>
          
          <View style={styles.inputContainer}>
            <Text style={styles.inputLabel}>Nome do Objetivo</Text>
            <TextInput
              style={styles.input}
              value={goal.name}
              onChangeText={(text) => setGoal({...goal, name: text})}
              placeholder="Ex: Casa própria"
              placeholderTextColor="#999"
            />
          </View>
          
          <View style={styles.inputContainer}>
            <Text style={styles.inputLabel}>Valor da Meta (R$)</Text>
            <TextInput
              style={styles.input}
              value={goal.targetAmount}
              onChangeText={(text) => setGoal({...goal, targetAmount: text})}
              keyboardType="numeric"
              placeholder="100000"
              placeholderTextColor="#999"
            />
          </View>
          
          <View style={styles.inputContainer}>
            <Text style={styles.inputLabel}>Valor Atual Disponível (R$)</Text>
            <TextInput
              style={styles.input}
              value={goal.currentAmount}
              onChangeText={(text) => setGoal({...goal, currentAmount: text})}
              keyboardType="numeric"
              placeholder="10000"
              placeholderTextColor="#999"
            />
          </View>
          
          <View style={styles.inputContainer}>
            <Text style={styles.inputLabel}>Prazo Desejado (meses)</Text>
            <TextInput
              style={styles.input}
              value={goal.monthsToGoal}
              onChangeText={(text) => setGoal({...goal, monthsToGoal: text})}
              keyboardType="numeric"
              placeholder="24"
              placeholderTextColor="#999"
            />
          </View>
          
          <View style={styles.inputContainer}>
            <Text style={styles.inputLabel}>Rentabilidade Esperada (% a.a.)</Text>
            <TextInput
              style={styles.input}
              value={goal.expectedReturn}
              onChangeText={(text) => setGoal({...goal, expectedReturn: text})}
              keyboardType="numeric"
              placeholder="12.0"
              placeholderTextColor="#999"
            />
          </View>
        </View>
        
        <TouchableOpacity style={styles.calculateButton} onPress={calculateGoal}>
          <Text style={styles.calculateButtonText}>Calcular Planejamento</Text>
        </TouchableOpacity>
        
        {results && (
          <View style={styles.resultsContainer}>
            <Text style={styles.resultsTitle}>📈 Planejamento para: {results.goalDetails.name}</Text>
            
            <View style={styles.mainResult}>
              <Text style={styles.mainAmount}>
                {formatCurrency(results.monthlyInvestment)}
              </Text>
              <Text style={styles.mainLabel}>
                Valor mensal necessário por {results.goalDetails.monthsToGoal} meses
              </Text>
            </View>
            
            <View style={styles.detailsContainer}>
              <View style={styles.detailRow}>
                <Text style={styles.detailLabel}>💰 Valor atual trabalhando:</Text>
                <Text style={styles.detailValue}>
                  {formatCurrency(results.futureValueOfCurrent)}
                </Text>
              </View>
              
              <View style={styles.detailRow}>
                <Text style={styles.detailLabel}>💵 Total a investir:</Text>
                <Text style={styles.detailValue}>
                  {formatCurrency(results.totalInvested)}
                </Text>
              </View>
            </View>
            
            <Text style={styles.scenariosTitle}>📊 Cenários Alternativos</Text>
            {results.scenarios.map((scenario, index) => (
              <View key={index} style={styles.scenarioCard}>
                <Text style={styles.scenarioLabel}>{scenario.label}</Text>
                <Text style={styles.scenarioMonths}>{scenario.months} meses</Text>
                <Text style={styles.scenarioAmount}>
                  {formatCurrency(scenario.monthlyPayment)}/mês
                </Text>
              </View>
            ))}
            
            <View style={styles.tipsContainer}>
              <Text style={styles.tipsTitle}>💡 Dicas para Alcançar sua Meta</Text>
              
              <View style={styles.tip}>
                <Text style={styles.tipIcon}>🔄</Text>
                <Text style={styles.tipText}>
                  <Text style={styles.tipBold}>Automatize seus aportes:</Text> Configure débito automático para investir todo mês sem falhas.
                </Text>
              </View>
              
              <View style={styles.tip}>
                <Text style={styles.tipIcon}>📈</Text>
                <Text style={styles.tipText}>
                  <Text style={styles.tipBold}>Revise periodicamente:</Text> Acompanhe o progresso e ajuste os valores se necessário.
                </Text>
              </View>
              
              <View style={styles.tip}>
                <Text style={styles.tipIcon}>🎯</Text>
                <Text style={styles.tipText}>
                  <Text style={styles.tipBold}>Seja realista:</Text> Escolha valores que cabem no seu orçamento mensal.
                </Text>
              </View>
              
              {results.monthlyInvestment > 1000 && (
                <View style={styles.tip}>
                  <Text style={styles.tipIcon}>⚠️</Text>
                  <Text style={styles.tipText}>
                    <Text style={styles.tipBold}>Valor alto:</Text> Considere estender o prazo ou aumentar a rentabilidade esperada.
                  </Text>
                </View>
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
  scrollContainer: {
    maxHeight: 600,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: COLORS.primaryDark,
    marginBottom: 10,
  },
  presetsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 15,
  },
  presetButton: {
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 10,
    width: '48%',
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#eee',
    alignItems: 'center',
  },
  presetName: {
    fontSize: 12,
    fontWeight: '600',
    color: COLORS.primaryDark,
    textAlign: 'center',
    marginBottom: 4,
  },
  presetAmount: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#27ae60',
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
    fontSize: 16,
    fontWeight: 'bold',
    color: COLORS.primaryDark,
    marginBottom: 15,
    textAlign: 'center',
  },
  mainResult: {
    backgroundColor: COLORS.primaryLight,
    borderRadius: 8,
    padding: 20,
    alignItems: 'center',
    marginBottom: 15,
  },
  mainAmount: {
    fontSize: 28,
    fontWeight: 'bold',
    color: COLORS.primaryDark,
  },
  mainLabel: {
    fontSize: 14,
    color: '#666',
    marginTop: 8,
    textAlign: 'center',
  },
  detailsContainer: {
    marginBottom: 15,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  detailLabel: {
    fontSize: 14,
    color: '#333',
    flex: 1,
  },
  detailValue: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.primaryDark,
  },
  scenariosTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: COLORS.primaryDark,
    marginBottom: 10,
  },
  scenarioCard: {
    backgroundColor: '#f9f9f9',
    borderRadius: 6,
    padding: 12,
    marginBottom: 8,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  scenarioLabel: {
    fontSize: 14,
    color: '#333',
    flex: 1,
  },
  scenarioMonths: {
    fontSize: 12,
    color: '#666',
    marginHorizontal: 10,
  },
  scenarioAmount: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.primaryDark,
  },
  tipsContainer: {
    backgroundColor: COLORS.primaryLight,
    borderRadius: 8,
    padding: 15,
    marginTop: 15,
  },
  tipsTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: COLORS.primaryDark,
    marginBottom: 12,
  },
  tip: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 10,
  },
  tipIcon: {
    fontSize: 16,
    marginRight: 8,
    marginTop: 2,
  },
  tipText: {
    fontSize: 14,
    lineHeight: 20,
    flex: 1,
  },
  tipBold: {
    fontWeight: 'bold',
    color: COLORS.primaryDark,
  },
});

export default FinancialGoalPlanner;