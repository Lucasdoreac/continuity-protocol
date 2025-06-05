import React, { useState } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  TouchableOpacity
} from 'react-native';
import { COLORS } from '../styles/globalStyles';
import { useColors } from '../contexts/ThemeContext';

const ProductComparison = () => {
  const [selectedCategory, setSelectedCategory] = useState('tesouro');
  
  // Definição dos produtos financeiros por categoria
  const products = {
    tesouro: [
      {
        name: "Tesouro Selic",
        risk: "Muito baixo",
        returnType: "Pós-fixado (Selic)",
        tax: "IR (15% a 22,5%)",
        minInvestment: "R$ 30,00",
        liquidity: "Alta (D+1)",
        protection: "Governo Federal",
        ideal: "Reserva de emergência, curto e médio prazo",
        pros: ["Segurança máxima", "Liquidez diária", "Investimento mínimo baixo"],
        cons: ["Rentabilidade limitada", "Incidência de IR"]
      },
      {
        name: "Tesouro IPCA+",
        risk: "Baixo",
        returnType: "Híbrido (IPCA + taxa prefixada)",
        tax: "IR (15% a 22,5%)",
        minInvestment: "R$ 30,00",
        liquidity: "Média (D+1, com volatilidade)",
        protection: "Governo Federal",
        ideal: "Médio e longo prazo, proteção contra inflação",
        pros: ["Proteção contra inflação", "Rentabilidade real conhecida", "Segurança"],
        cons: ["Volatilidade no preço", "Menos adequado para resgate antes do vencimento"]
      },
      {
        name: "Tesouro Prefixado",
        risk: "Baixo a médio",
        returnType: "Prefixado",
        tax: "IR (15% a 22,5%)",
        minInvestment: "R$ 30,00",
        liquidity: "Média (D+1, com volatilidade)",
        protection: "Governo Federal",
        ideal: "Médio prazo, cenário de queda de juros",
        pros: ["Rentabilidade conhecida antecipadamente", "Segurança"],
        cons: ["Maior volatilidade", "Perde atratividade em cenário de alta de juros"]
      }
    ],
    bancarios: [
      {
        name: "CDB (banco grande)",
        risk: "Baixo",
        returnType: "Pós, pré ou híbrido",
        tax: "IR (15% a 22,5%)",
        minInvestment: "R$ 50,00 a R$ 500,00",
        liquidity: "Varia (D+0 a D+1 até vencimento)",
        protection: "FGC (até R$ 250 mil por CPF/CNPJ)",
        ideal: "Reserva, diversificação de renda fixa",
        pros: ["Diversidade de opções", "Boa segurança", "Rentabilidade superior ao Tesouro em alguns casos"],
        cons: ["Mínimo maior em alguns bancos", "Resgate antecipado nem sempre disponível"]
      },
      {
        name: "LCI/LCA",
        risk: "Baixo",
        returnType: "Geralmente pós-fixado",
        tax: "Isento de IR",
        minInvestment: "R$ 1.000,00 (média)",
        liquidity: "Baixa (carência, resgate no vencimento)",
        protection: "FGC (até R$ 250 mil por CPF/CNPJ)",
        ideal: "Médio prazo, vantagem fiscal",
        pros: ["Isenção de IR", "Boa rentabilidade líquida"],
        cons: ["Liquidez restrita", "Mínimo mais alto", "Carência"]
      },
      {
        name: "Poupança",
        risk: "Muito baixo",
        returnType: "Regra específica (70% da Selic quando > 8,5%)",
        tax: "Isento de IR",
        minInvestment: "R$ 1,00",
        liquidity: "Alta (D+0, aniversário para rendimento)",
        protection: "FGC (até R$ 250 mil por CPF/CNPJ)",
        ideal: "Iniciantes, valores muito pequenos",
        pros: ["Simplicidade", "Liquidez imediata", "Isento de IR"],
        cons: ["Menor rentabilidade entre RF", "Perde da inflação em muitos períodos"]
      }
    ],
    fundos: [
      {
        name: "Fundo DI",
        risk: "Baixo",
        returnType: "Pós-fixado (CDI)",
        tax: "IR (15% a 22,5%) + taxa de adm",
        minInvestment: "R$ 100,00 (média)",
        liquidity: "Alta (D+0 a D+1)",
        protection: "Sem garantia específica",
        ideal: "Alternativa simples à renda fixa direta",
        pros: ["Gestão profissional", "Praticidade", "Diversificação automática"],
        cons: ["Taxa de administração", "Rentabilidade menor que títulos diretos equivalentes"]
      },
      {
        name: "Fundo Multimercado",
        risk: "Médio a alto",
        returnType: "Variável (depende da estratégia)",
        tax: "IR (15% a 22,5%) + taxas",
        minInvestment: "R$ 500,00 a R$ 5.000,00",
        liquidity: "Média (D+1 a D+30, conforme regras)",
        protection: "Sem garantia específica",
        ideal: "Diversificação, exposição a múltiplas estratégias",
        pros: ["Gestão especializada", "Acesso a estratégias complexas", "Diversificação em um só produto"],
        cons: ["Taxas mais altas", "Risco maior", "Mínimo mais elevado"]
      },
      {
        name: "ETF Ibovespa",
        risk: "Alto",
        returnType: "Variável (segue índice)",
        tax: "15% sobre ganho capital",
        minInvestment: "Preço de 1 cota (~R$ 100)",
        liquidity: "Alta (D+2, negociado em bolsa)",
        protection: "Sem garantia específica",
        ideal: "Exposição a ações com simplicidade",
        pros: ["Diversificação em ações", "Taxas baixas", "Simplicidade"],
        cons: ["Volatilidade", "Risco de mercado", "Não tem gestão ativa"]
      }
    ]
  };
  
  // Retorna os produtos da categoria selecionada
  const getSelectedProducts = () => {
    return products[selectedCategory] || [];
  };
  
  return (
    <View style={styles.container}>
      <Text style={styles.title}>📊 Comparativo de Investimentos</Text>
      <Text style={styles.description}>
        Compare os principais produtos financeiros para iniciantes e encontre os mais adequados 
        para seus objetivos.
      </Text>
      
      <View style={styles.categoryButtons}>
        <TouchableOpacity 
          style={[
            styles.categoryButton, 
            selectedCategory === 'tesouro' && styles.selectedCategoryButton
          ]}
          onPress={() => setSelectedCategory('tesouro')}
        >
          <Text 
            style={[
              styles.categoryButtonText, 
              selectedCategory === 'tesouro' && styles.selectedCategoryButtonText
            ]}
          >
            Tesouro Direto
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[
            styles.categoryButton, 
            selectedCategory === 'bancarios' && styles.selectedCategoryButton
          ]}
          onPress={() => setSelectedCategory('bancarios')}
        >
          <Text 
            style={[
              styles.categoryButtonText, 
              selectedCategory === 'bancarios' && styles.selectedCategoryButtonText
            ]}
          >
            Bancários
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[
            styles.categoryButton, 
            selectedCategory === 'fundos' && styles.selectedCategoryButton
          ]}
          onPress={() => setSelectedCategory('fundos')}
        >
          <Text 
            style={[
              styles.categoryButtonText, 
              selectedCategory === 'fundos' && styles.selectedCategoryButtonText
            ]}
          >
            Fundos
          </Text>
        </TouchableOpacity>
      </View>
      
      <View style={styles.productsContainer}>
        {getSelectedProducts().map((product, index) => (
          <View key={index} style={styles.productCard}>
            <Text style={styles.productName}>{product.name}</Text>
            
            <View style={styles.productDetails}>
              <View style={styles.detailRow}>
                <Text style={styles.detailLabel}>Risco:</Text>
                <Text style={styles.detailValue}>{product.risk}</Text>
              </View>
              
              <View style={styles.detailRow}>
                <Text style={styles.detailLabel}>Rentabilidade:</Text>
                <Text style={styles.detailValue}>{product.returnType}</Text>
              </View>
              
              <View style={styles.detailRow}>
                <Text style={styles.detailLabel}>Tributação:</Text>
                <Text style={styles.detailValue}>{product.tax}</Text>
              </View>
              
              <View style={styles.detailRow}>
                <Text style={styles.detailLabel}>Investimento mínimo:</Text>
                <Text style={styles.detailValue}>{product.minInvestment}</Text>
              </View>
              
              <View style={styles.detailRow}>
                <Text style={styles.detailLabel}>Liquidez:</Text>
                <Text style={styles.detailValue}>{product.liquidity}</Text>
              </View>
              
              <View style={styles.detailRow}>
                <Text style={styles.detailLabel}>Proteção:</Text>
                <Text style={styles.detailValue}>{product.protection}</Text>
              </View>
              
              <View style={styles.detailRow}>
                <Text style={styles.detailLabel}>Ideal para:</Text>
                <Text style={styles.detailValue}>{product.ideal}</Text>
              </View>
            </View>
            
            <View style={styles.prosConsContainer}>
              <View style={styles.prosContainer}>
                <Text style={styles.prosConsTitle}>✅ Vantagens:</Text>
                {product.pros.map((pro, i) => (
                  <Text key={i} style={styles.proConItem}>• {pro}</Text>
                ))}
              </View>
              
              <View style={styles.consContainer}>
                <Text style={styles.prosConsTitle}>⚠️ Limitações:</Text>
                {product.cons.map((con, i) => (
                  <Text key={i} style={styles.proConItem}>• {con}</Text>
                ))}
              </View>
            </View>
          </View>
        ))}
      </View>
      
      <View style={styles.infoBox}>
        <Text style={styles.infoTitle}>💡 Dica</Text>
        <Text style={styles.infoText}>
          <Text style={styles.highlight}>Iniciantes geralmente começam com Tesouro Selic e CDBs</Text> pela 
          simplicidade e baixo risco. Conforme adquirem conhecimento, podem gradualmente 
          diversificar a carteira com outros produtos.
        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: COLORS.white,
    borderRadius: 8,
    padding: 15,
    marginVertical: 15,
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
  },
  categoryButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 15,
  },
  categoryButton: {
    backgroundColor: '#f0f0f0',
    paddingVertical: 10,
    paddingHorizontal: 15,
    borderRadius: 5,
    flex: 1,
    marginHorizontal: 5,
    alignItems: 'center',
  },
  selectedCategoryButton: {
    backgroundColor: COLORS.primaryDark,
  },
  categoryButtonText: {
    fontWeight: 'bold',
    color: '#555',
    fontSize: 12,
  },
  selectedCategoryButtonText: {
    color: COLORS.white,
  },
  productsContainer: {
    // Removido maxHeight e ScrollView - agora usa View normal
  },
  productCard: {
    backgroundColor: '#f9f9f9',
    borderRadius: 8,
    padding: 15,
    marginBottom: 15,
    borderLeftWidth: 4,
    borderLeftColor: COLORS.primaryDark,
  },
  productName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.primaryDark,
    marginBottom: 10,
  },
  productDetails: {
    marginBottom: 15,
  },
  detailRow: {
    flexDirection: 'row',
    marginBottom: 5,
    flexWrap: 'wrap',
  },
  detailLabel: {
    fontWeight: 'bold',
    width: '40%',
    fontSize: 14,
    minWidth: 120,
  },
  detailValue: {
    flex: 1,
    fontSize: 14,
    flexShrink: 1,
  },
  prosConsContainer: {
    marginTop: 10,
  },
  prosConsTitle: {
    fontWeight: 'bold',
    fontSize: 16,
    marginBottom: 5,
    color: COLORS.primaryDark,
  },
  proConItem: {
    fontSize: 14,
    marginBottom: 3,
    paddingLeft: 5,
    lineHeight: 20,
  },
  prosContainer: {
    marginBottom: 10,
  },
  consContainer: {
    marginBottom: 5,
  },
  infoBox: {
    backgroundColor: COLORS.primaryLight,
    borderRadius: 8,
    padding: 15,
    marginTop: 15,
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: COLORS.primaryDark,
    marginBottom: 10,
  },
  infoText: {
    fontSize: 14,
    lineHeight: 20,
  },
  highlight: {
    fontWeight: 'bold',
    color: COLORS.primaryDark,
  }
});

export default ProductComparison;