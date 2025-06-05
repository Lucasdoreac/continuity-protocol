import React, { useState } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  TouchableOpacity
} from 'react-native';
import { COLORS } from '../styles/globalStyles';
import AnalyticsService from '../services/AnalyticsService';

const InvestorProfileQuiz = ({ onProfileDetermined }) => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState([]);
  const [quizCompleted, setQuizCompleted] = useState(false);
  const [profile, setProfile] = useState(null);
  
  // Definição das perguntas e opções de resposta
  const questions = [
    {
      question: "Como você reagiria a uma queda de 30% em seus investimentos?",
      options: [
        { text: "Venderia tudo imediatamente para evitar perdas maiores", points: -10 },
        { text: "Venderia parte para reduzir a exposição ao risco", points: 0 },
        { text: "Manteria a estratégia e esperaria a recuperação", points: 10 },
        { text: "Compraria mais aproveitando os preços menores", points: 20 }
      ]
    },
    {
      question: "Por quanto tempo você pretende manter seus investimentos?",
      options: [
        { text: "Menos de 1 ano", points: 0 },
        { text: "1 a 3 anos", points: 5 },
        { text: "3 a 7 anos", points: 10 },
        { text: "Mais de 7 anos", points: 20 }
      ]
    },
    {
      question: "Qual é o seu principal objetivo ao investir?",
      options: [
        { text: "Preservar capital com segurança máxima", points: 0 },
        { text: "Obter retorno um pouco acima da poupança com baixo risco", points: 5 },
        { text: "Crescimento moderado com riscos controlados", points: 10 },
        { text: "Maximizar retorno, aceitando maior volatilidade", points: 20 }
      ]
    },
    {
      question: "Qual percentual da sua renda mensal você consegue investir?",
      options: [
        { text: "Até 10% da minha renda", points: 5 },
        { text: "Entre 10% e 20% da minha renda", points: 10 },
        { text: "Entre 20% e 30% da minha renda", points: 15 },
        { text: "Mais de 30% da minha renda", points: 20 }
      ]
    },
    {
      question: "Qual afirmação melhor representa sua experiência com investimentos?",
      options: [
        { text: "Nunca investi ou só tenho poupança", points: 0 },
        { text: "Conheço renda fixa mas nunca investi em ações", points: 5 },
        { text: "Já invisto em renda fixa e um pouco em ações", points: 10 },
        { text: "Tenho experiência com diversos tipos de investimentos", points: 15 }
      ]
    }
  ];
  
  // Perfis possíveis baseados na pontuação
  const profiles = [
    { 
      type: "Conservador", 
      min: 0, 
      max: 30,
      description: "Prioriza segurança e estabilidade. Prefere investimentos com risco mínimo, mesmo com retornos menores.",
      recommendation: "Foco em Tesouro Direto, CDBs de bancos grandes e fundos DI. Ações limitadas a 10% da carteira, se houver."
    },
    { 
      type: "Moderado", 
      min: 31, 
      max: 60,
      description: "Busca equilíbrio entre segurança e rentabilidade. Aceita alguma volatilidade para obter retornos melhores.",
      recommendation: "60-70% em renda fixa, 20-30% em ações ou ETFs e 10% em fundos imobiliários."
    },
    { 
      type: "Arrojado", 
      min: 61, 
      max: 100,
      description: "Prioriza retornos maiores a longo prazo. Tem conforto com volatilidade e entende os riscos envolvidos.",
      recommendation: "40-50% em renda fixa, 40-50% em ações ou ETFs e 10-20% em investimentos alternativos."
    }
  ];
  
  // Função para registrar a resposta e avançar para a próxima pergunta
  const handleAnswer = (pointsValue) => {
    const newAnswers = [...answers, pointsValue];
    setAnswers(newAnswers);
    
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      // Última pergunta respondida, calcular o perfil
      calculateProfile(newAnswers);
    }
  };
  
  // Calcula o perfil baseado nas respostas
  const calculateProfile = async (answers) => {
    const totalPoints = answers.reduce((sum, points) => sum + points, 0);
    
    // 📊 ANALYTICS: Quiz iniciado
    await AnalyticsService.logEvent(AnalyticsService.EVENTS.QUIZ_STARTED, {
      total_questions: questions.length,
      quiz_type: 'investor_profile'
    });
    
    // Determina o perfil com base no total de pontos
    const determinedProfile = profiles.find(
      profile => totalPoints >= profile.min && totalPoints <= profile.max
    );
    
    setProfile(determinedProfile);
    setQuizCompleted(true);
    
    // 📊 ANALYTICS: Quiz completado + Perfil identificado
    await AnalyticsService.logQuizCompleted(determinedProfile.type);
    await AnalyticsService.logEvent(AnalyticsService.EVENTS.PROFILE_IDENTIFIED, {
      profile_type: determinedProfile.type,
      profile_name: determinedProfile.name,
      total_points: totalPoints,
      answers_count: answers.length
    });
    
    // Configurar propriedades do usuário para personalização
    await AnalyticsService.setUserProfile({
      type: determinedProfile.type,
      experience: determinedProfile.experience || 'calculado',
      goal: 'educacao_financeira',
      firstAccess: new Date().toISOString()
    });
    
    // Notifica o componente pai sobre o perfil determinado
    if (onProfileDetermined) {
      onProfileDetermined(determinedProfile);
    }
  };
  
  // Reinicia o quiz
  const restartQuiz = () => {
    setCurrentQuestion(0);
    setAnswers([]);
    setQuizCompleted(false);
    setProfile(null);
  };
  
  return (
    <View style={styles.container}>
      {!quizCompleted ? (
        <View style={styles.quizContainer}>
          <Text style={styles.questionCounter}>Pergunta {currentQuestion + 1} de {questions.length}</Text>
          
          <Text style={styles.questionText}>
            {questions[currentQuestion].question}
          </Text>
          
          <View style={styles.optionsContainer}>
            {questions[currentQuestion].options.map((option, index) => (
              <TouchableOpacity
                key={index}
                style={styles.optionButton}
                onPress={() => handleAnswer(option.points)}
              >
                <Text style={styles.optionText}>{option.text}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      ) : (
        <View style={styles.resultContainer}>
          <View style={styles.profileHeader}>
            <Text style={styles.profileTitle}>Seu Perfil de Investidor:</Text>
            <Text style={styles.profileType}>{profile?.type || 'Calculando...'}</Text>
          </View>
          
          <View style={styles.profileDetails}>
            <Text style={styles.profileDescription}>{profile?.description || ''}</Text>
            
            <Text style={styles.recommendationTitle}>📊 Recomendações para seu perfil:</Text>
            <Text style={styles.recommendationText}>{profile?.recommendation || ''}</Text>
            
            <View style={styles.riskMeter}>
              <Text style={styles.riskMeterLabel}>Nível de Risco:</Text>
              <View style={styles.riskMeterBar}>
                <View 
                  style={[
                    styles.riskMeterFill, 
                    { 
                      width: `${profile?.type === 'Conservador' ? 30 : 
                              profile?.type === 'Moderado' ? 65 : 95}%`
                    }
                  ]} 
                />
              </View>
              <View style={styles.riskMeterLabels}>
                <Text>Baixo</Text>
                <Text>Médio</Text>
                <Text>Alto</Text>
              </View>
            </View>
          </View>
          
          <TouchableOpacity style={styles.restartButton} onPress={restartQuiz}>
            <Text style={styles.restartButtonText}>Refazer o Teste</Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: COLORS.white,
    borderRadius: 8,
    padding: 15,
    marginVertical: 10,
    shadowColor: COLORS.black,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  quizContainer: {
    padding: 5,
  },
  questionCounter: {
    fontSize: 14,
    color: '#888',
    marginBottom: 15,
    textAlign: 'center',
  },
  questionText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.primaryDark,
    marginBottom: 20,
    textAlign: 'center',
  },
  optionsContainer: {
    marginBottom: 15,
  },
  optionButton: {
    backgroundColor: COLORS.primaryLight,
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
  },
  optionText: {
    fontSize: 15,
    color: COLORS.primaryDark,
  },
  resultContainer: {
    padding: 10,
  },
  profileHeader: {
    alignItems: 'center',
    marginBottom: 20,
  },
  profileTitle: {
    fontSize: 18,
    color: COLORS.primaryDark,
    marginBottom: 5,
  },
  profileType: {
    fontSize: 26,
    fontWeight: 'bold',
    color: COLORS.primaryDark,
  },
  profileDetails: {
    backgroundColor: '#f9f9f9',
    borderRadius: 8,
    padding: 15,
    marginBottom: 20,
  },
  profileDescription: {
    fontSize: 16,
    lineHeight: 24,
    marginBottom: 20,
  },
  recommendationTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.primaryDark,
    marginBottom: 10,
  },
  recommendationText: {
    fontSize: 16,
    lineHeight: 24,
    marginBottom: 20,
  },
  riskMeter: {
    marginTop: 10,
  },
  riskMeterLabel: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10,
    color: COLORS.primaryDark,
  },
  riskMeterBar: {
    height: 10,
    backgroundColor: '#e0e0e0',
    borderRadius: 5,
    overflow: 'hidden',
  },
  riskMeterFill: {
    height: '100%',
    backgroundColor: COLORS.primaryDark,
    borderRadius: 5,
  },
  riskMeterLabels: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 5,
  },
  restartButton: {
    backgroundColor: COLORS.primaryDark,
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 10,
  },
  restartButtonText: {
    color: COLORS.white,
    fontWeight: 'bold',
    fontSize: 16,
  },
});

export default InvestorProfileQuiz;
