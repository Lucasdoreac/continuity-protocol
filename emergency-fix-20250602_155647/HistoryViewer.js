import React, { useState } from 'react';
import { 
  View, 
  Text, 
  ScrollView,
  TouchableOpacity, 
  StyleSheet, 
  Alert 
} from 'react-native';
import { useHistory } from '../contexts/HistoryContext';
import { COLORS } from '../styles/globalStyles';

const HistoryViewer = ({ filterByTool = null }) => {
  const { 
    history, 
    getHistoryByType, 
    removeFromHistory, 
    clearHistory,
    exportToJSON,
    exportToCSV,
    copyToClipboard 
  } = useHistory();
  
  const [selectedTool, setSelectedTool] = useState(filterByTool || 'all');
  
  // Obter dados filtrados
  const filteredHistory = selectedTool === 'all' 
    ? history 
    : getHistoryByType(selectedTool);
  
  // Obter tipos únicos de ferramentas
  const toolTypes = [...new Set(history.map(item => item.toolType))];
  
  // Formatar data
  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleString('pt-BR');
  };
  
  // Exportar histórico filtrado
  const handleExport = (format) => {
    const items = filteredHistory;
    if (items.length === 0) {
      Alert.alert('📭 Histórico Vazio', 'Não há dados para exportar');
      return;
    }
    
    if (format === 'json') {
      const jsonData = exportToJSON(items);
      copyToClipboard(jsonData).then(success => {
        if (success) {
          Alert.alert('✅ JSON Copiado', 'Dados JSON copiados para área de transferência');
        }
      });
    } else if (format === 'csv') {
      const csvData = exportToCSV(items);
      copyToClipboard(csvData).then(success => {
        if (success) {
          Alert.alert('✅ CSV Copiado', 'Dados CSV copiados para área de transferência');
        }
      });
    }
  };
  
  // Copiar item específico
  const handleCopyItem = (item) => {
    const text = JSON.stringify(item, null, 2);
    copyToClipboard(text).then(success => {
      if (success) {
        Alert.alert('✅ Copiado', 'Item copiado para área de transferência');
      }
    });
  };
  
  // Remover item específico
  const handleRemoveItem = (id) => {
    Alert.alert(
      '🗑️ Remover Item',
      'Tem certeza que deseja remover este item do histórico?',
      [
        { text: 'Cancelar', style: 'cancel' },
        { 
          text: 'Remover', 
          style: 'destructive',
          onPress: () => removeFromHistory(id)
        }
      ]
    );
  };
  
  // Limpar todo histórico
  const handleClearAll = () => {
    Alert.alert(
      '🗑️ Limpar Histórico',
      'Tem certeza que deseja limpar todo o histórico? Esta ação não pode ser desfeita.',
      [
        { text: 'Cancelar', style: 'cancel' },
        { 
          text: 'Limpar Tudo', 
          style: 'destructive',
          onPress: clearHistory
        }
      ]
    );
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>📚 Histórico de Ferramentas</Text>
        <TouchableOpacity 
          style={styles.clearButton}
          onPress={handleClearAll}
        >
          <Text style={styles.clearButtonText}>🗑️ Limpar</Text>
        </TouchableOpacity>
      </View>

      {/* Exportar */}
      <View style={styles.exportButtons}>
        <TouchableOpacity 
          style={styles.exportButton}
          onPress={() => handleExport('json')}
        >
          <Text style={styles.exportButtonText}>📄 Copiar JSON</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={styles.exportButton}
          onPress={() => handleExport('csv')}
        >
          <Text style={styles.exportButtonText}>📊 Copiar CSV</Text>
        </TouchableOpacity>
      </View>

      {/* Filtros */}
      {toolTypes.length > 0 && (
        <View style={styles.filterContainer}>
          <Text style={styles.filterTitle}>🔍 Filtrar por ferramenta:</Text>
          <View style={styles.filterButtons}>
            <TouchableOpacity
              style={[
                styles.filterButton,
                selectedTool === 'all' && styles.filterButtonActive
              ]}
              onPress={() => setSelectedTool('all')}
            >
              <Text style={[
                styles.filterButtonText,
                selectedTool === 'all' && styles.filterButtonTextActive
              ]}>
                📋 Todas ({history.length})
              </Text>
            </TouchableOpacity>
            
            {toolTypes.map(toolType => (
              <TouchableOpacity
                key={toolType}
                style={[
                  styles.filterButton,
                  selectedTool === toolType && styles.filterButtonActive
                ]}
                onPress={() => setSelectedTool(toolType)}
              >
                <Text style={[
                  styles.filterButtonText,
                  selectedTool === toolType && styles.filterButtonTextActive
                ]}>
                  {toolType} ({getHistoryByType(toolType).length})
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      )}

      {/* Lista do histórico */}
      <ScrollView style={styles.historyList} showsVerticalScrollIndicator={false}>
        {filteredHistory.length === 0 ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyText}>
              📭 Nenhum histórico encontrado
              {selectedTool !== 'all' ? ` para ${selectedTool}` : ''}
              {'\n\n'}
              Use as ferramentas dos capítulos e salve no histórico para vê-las aqui.
            </Text>
          </View>
        ) : (
          filteredHistory.map(item => (
            <View key={item.id} style={styles.historyItem}>
              <View style={styles.itemHeader}>
                <Text style={styles.itemType}>{item.toolType}</Text>
                <Text style={styles.itemDate}>{formatDate(item.timestamp)}</Text>
              </View>
              
              {item.description && (
                <Text style={styles.itemDescription}>{item.description}</Text>
              )}
              
              <View style={styles.itemActions}>
                <TouchableOpacity 
                  style={styles.itemButton}
                  onPress={() => handleCopyItem(item)}
                >
                  <Text style={styles.itemButtonText}>📋 Copiar</Text>
                </TouchableOpacity>
                
                <TouchableOpacity 
                  style={[styles.itemButton, styles.removeButton]}
                  onPress={() => handleRemoveItem(item.id)}
                >
                  <Text style={styles.itemButtonText}>🗑️ Remover</Text>
                </TouchableOpacity>
              </View>
            </View>
          ))
        )}
      </ScrollView>
    </View>
  );
};
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 16,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
    paddingVertical: 12,
    paddingHorizontal: 16,
    backgroundColor: 'white',
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 2,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: COLORS.primary,
  },
  clearButton: {
    backgroundColor: '#ff4444',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 6,
  },
  clearButtonText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 14,
  },
  exportButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 16,
    paddingVertical: 12,
    backgroundColor: 'white',
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 2,
  },
  exportButton: {
    backgroundColor: COLORS.secondary,
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 6,
    flex: 1,
    marginHorizontal: 4,
  },
  exportButtonText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 14,
    textAlign: 'center',
  },
  filterContainer: {
    marginBottom: 16,
  },
  filterTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: COLORS.primary,
    marginBottom: 8,
  },
  filterButtons: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  filterButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: COLORS.secondary,
    backgroundColor: 'white',
  },
  filterButtonActive: {
    backgroundColor: COLORS.secondary,
  },
  filterButtonText: {
    color: COLORS.secondary,
    fontSize: 12,
    fontWeight: 'bold',
  },
  filterButtonTextActive: {
    color: 'white',
  },
  historyList: {
    flex: 1,
  },
  historyItem: {
    backgroundColor: 'white',
    marginBottom: 12,
    padding: 16,
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 2,
  },
  itemHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  itemType: {
    fontSize: 16,
    fontWeight: 'bold',
    color: COLORS.primary,
  },
  itemDate: {
    fontSize: 12,
    color: '#666',
  },
  itemDescription: {
    fontSize: 14,
    color: '#333',
    marginBottom: 12,
    lineHeight: 20,
  },
  itemActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 12,
  },
  itemButton: {
    flex: 1,
    backgroundColor: COLORS.accent || COLORS.secondary,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 6,
    alignItems: 'center',
  },
  removeButton: {
    backgroundColor: '#ff4444',
  },
  itemButtonText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 12,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 40,
  },
  emptyText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    lineHeight: 24,
  },
});

export default HistoryViewer;