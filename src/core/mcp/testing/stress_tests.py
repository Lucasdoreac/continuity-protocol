#!/usr/bin/env python3
"""
Stress Tests - Continuity Protocol
Testes de stress para o Continuity Protocol
"""

import os
import sys
import json
import time
import random
import threading
import unittest
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

# Adicionar diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Importar componentes
try:
    from core.mcp.integration_v2 import enhanced_context_protocol
    from core.mcp.versioning import versioning_system
    from core.mcp.backup import backup_system
    from core.mcp.notification import notification_system
    from core.mcp.search import search_system
except ImportError:
    print("Erro ao importar componentes do Continuity Protocol")
    sys.exit(1)

class StressTests(unittest.TestCase):
    """
    Testes de stress para o Continuity Protocol
    """
    
    @classmethod
    def setUpClass(cls):
        """Configuração inicial para os testes"""
        cls.project_id = f"stress-test-{int(time.time())}"
        cls.project_name = "Stress Test Project"
        cls.project_description = "Project for stress tests"
        
        # Registrar projeto de teste
        cls.project_info = enhanced_context_protocol.register_project(
            cls.project_id,
            cls.project_name,
            cls.project_description
        )
        
        print(f"Projeto de teste criado: {cls.project_id}")
        
        # Criar backup antes dos testes
        backup_result = backup_system.create_backup(
            "full",
            "Backup before stress tests"
        )
        
        print(f"Backup criado: {backup_result.get('backup_info', {}).get('id', 'unknown')}")
    
    @classmethod
    def tearDownClass(cls):
        """Limpeza após os testes"""
        # Criar backup após os testes
        backup_result = backup_system.create_backup(
            "full",
            "Backup after stress tests"
        )
        
        print(f"Backup final criado: {backup_result.get('backup_info', {}).get('id', 'unknown')}")
        
        # Reindexar todos os artefatos
        reindex_result = enhanced_context_protocol.reindex_all_artifacts()
        
        print(f"Reindexação concluída: {reindex_result.get('indexed_count', 0)} artefatos indexados")
    
    def test_01_bulk_artifact_creation(self):
        """Teste de criação em massa de artefatos"""
        # Número de artefatos a serem criados
        num_artifacts = 50
        
        # Tipos de artefatos
        artifact_types = ["document", "code", "plan", "test", "analysis"]
        
        # Criar artefatos
        start_time = time.time()
        artifacts = []
        
        for i in range(num_artifacts):
            # Selecionar tipo aleatório
            artifact_type = random.choice(artifact_types)
            
            # Criar conteúdo
            content = f"# Stress Test {artifact_type.capitalize()} {i}\n\n"
            content += f"This is a {artifact_type} for stress testing.\n\n"
            
            # Adicionar conteúdo adicional para aumentar tamanho
            for j in range(10):
                content += f"Section {j+1}: Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n"
            
            # Criar metadados
            metadata = {
                "title": f"Stress Test {artifact_type.capitalize()} {i}",
                "description": f"{artifact_type.capitalize()} for stress testing",
                "version": "1.0.0",
                "stress_index": i,
                "artifact_type": artifact_type
            }
            
            # Armazenar artefato
            artifact_info = enhanced_context_protocol.store_artifact(
                content,
                artifact_type,
                self.project_id,
                "stress_tests",
                metadata
            )
            
            artifacts.append(artifact_info)
            
            # Verificar se artefato foi criado
            self.assertIsNotNone(artifact_info)
            self.assertIn("id", artifact_info)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Verificar se todos os artefatos foram criados
        self.assertEqual(len(artifacts), num_artifacts)
        
        # Imprimir estatísticas
        print(f"Criados {num_artifacts} artefatos em {elapsed_time:.2f} segundos")
        print(f"Média de {elapsed_time/num_artifacts:.4f} segundos por artefato")
        
        # Salvar IDs dos artefatos para testes posteriores
        self.__class__.artifact_ids = [a["id"] for a in artifacts]
    
    def test_02_bulk_versioning(self):
        """Teste de versionamento em massa"""
        # Verificar se os IDs dos artefatos estão disponíveis
        self.assertTrue(hasattr(self.__class__, "artifact_ids"), "Artifact IDs not available")
        
        # Selecionar uma amostra de artefatos para versionamento
        sample_size = min(20, len(self.__class__.artifact_ids))
        sample_ids = random.sample(self.__class__.artifact_ids, sample_size)
        
        # Criar novas versões
        start_time = time.time()
        versions = []
        
        for artifact_id in sample_ids:
            # Obter artefato
            artifact = enhanced_context_protocol.get_artifact(artifact_id)
            
            if not artifact:
                continue
            
            # Atualizar conteúdo
            updated_content = artifact["content"] + f"\n\nUpdated at {datetime.now().isoformat()}"
            
            # Atualizar artefato
            update_result = enhanced_context_protocol.update_artifact(
                artifact_id,
                updated_content,
                "stress_tests",
                artifact.get("metadata", {}),
                "minor",
                "Update for stress testing"
            )
            
            versions.append(update_result)
            
            # Verificar se atualização foi bem-sucedida
            self.assertTrue(update_result["success"])
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Verificar se todas as versões foram criadas
        self.assertEqual(len(versions), len(sample_ids))
        
        # Imprimir estatísticas
        print(f"Criadas {len(versions)} versões em {elapsed_time:.2f} segundos")
        print(f"Média de {elapsed_time/len(versions):.4f} segundos por versão")
    
    def test_03_concurrent_operations(self):
        """Teste de operações concorrentes"""
        # Verificar se os IDs dos artefatos estão disponíveis
        self.assertTrue(hasattr(self.__class__, "artifact_ids"), "Artifact IDs not available")
        
        # Número de threads
        num_threads = 5
        
        # Operações por thread
        operations_per_thread = 10
        
        # Resultados
        results = []
        
        # Função para executar operações em uma thread
        def run_operations(thread_id):
            thread_results = []
            
            for i in range(operations_per_thread):
                # Selecionar operação aleatória
                operation = random.choice(["get", "search", "version", "notification"])
                
                try:
                    if operation == "get":
                        # Obter artefato aleatório
                        artifact_id = random.choice(self.__class__.artifact_ids)
                        artifact = enhanced_context_protocol.get_artifact(artifact_id)
                        thread_results.append({"operation": "get", "success": artifact is not None})
                    
                    elif operation == "search":
                        # Buscar por termo aleatório
                        terms = ["stress", "test", "lorem", "ipsum", "section"]
                        term = random.choice(terms)
                        search_result = enhanced_context_protocol.search_artifacts(term)
                        thread_results.append({"operation": "search", "success": search_result["success"]})
                    
                    elif operation == "version":
                        # Obter histórico de versões de artefato aleatório
                        artifact_id = random.choice(self.__class__.artifact_ids)
                        history_result = enhanced_context_protocol.get_artifact_history(artifact_id)
                        thread_results.append({"operation": "version", "success": history_result["success"]})
                    
                    elif operation == "notification":
                        # Criar notificação
                        notification_result = enhanced_context_protocol.create_notification(
                            f"Thread {thread_id} Notification {i}",
                            f"Notification from thread {thread_id}, operation {i}",
                            "info",
                            "stress_tests",
                            {"thread_id": thread_id, "operation_index": i}
                        )
                        thread_results.append({"operation": "notification", "success": notification_result["success"]})
                
                except Exception as e:
                    thread_results.append({"operation": operation, "success": False, "error": str(e)})
            
            return thread_results
        
        # Criar e iniciar threads
        threads = []
        start_time = time.time()
        
        for i in range(num_threads):
            thread = threading.Thread(target=lambda i=i: results.extend(run_operations(i)))
            threads.append(thread)
            thread.start()
        
        # Aguardar threads
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Verificar resultados
        total_operations = len(results)
        successful_operations = sum(1 for r in results if r["success"])
        
        # Imprimir estatísticas
        print(f"Executadas {total_operations} operações concorrentes em {elapsed_time:.2f} segundos")
        print(f"Operações bem-sucedidas: {successful_operations} ({successful_operations/total_operations*100:.2f}%)")
        print(f"Média de {elapsed_time/total_operations:.4f} segundos por operação")
        
        # Verificar se a maioria das operações foi bem-sucedida
        self.assertGreaterEqual(successful_operations / total_operations, 0.9)
    
    def test_04_search_performance(self):
        """Teste de performance de busca"""
        # Termos de busca
        search_terms = ["stress", "test", "lorem", "ipsum", "section", "document", "code", "plan"]
        
        # Executar buscas
        start_time = time.time()
        search_results = []
        
        for term in search_terms:
            result = enhanced_context_protocol.search_artifacts(term)
            search_results.append(result)
            
            # Verificar se busca foi bem-sucedida
            self.assertTrue(result["success"])
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Calcular estatísticas
        total_results = sum(len(r["results"]) for r in search_results)
        
        # Imprimir estatísticas
        print(f"Executadas {len(search_terms)} buscas em {elapsed_time:.2f} segundos")
        print(f"Total de resultados: {total_results}")
        print(f"Média de {elapsed_time/len(search_terms):.4f} segundos por busca")
        
        # Verificar se todas as buscas retornaram resultados
        for result in search_results:
            self.assertGreater(len(result["results"]), 0)
    
    def test_05_notification_performance(self):
        """Teste de performance de notificações"""
        # Número de notificações
        num_notifications = 50
        
        # Criar notificações
        start_time = time.time()
        notification_results = []
        
        for i in range(num_notifications):
            result = enhanced_context_protocol.create_notification(
                f"Performance Test Notification {i}",
                f"This is notification {i} for performance testing",
                "info",
                "stress_tests",
                {"index": i}
            )
            
            notification_results.append(result)
            
            # Verificar se notificação foi criada
            self.assertTrue(result["success"])
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Imprimir estatísticas
        print(f"Criadas {num_notifications} notificações em {elapsed_time:.2f} segundos")
        print(f"Média de {elapsed_time/num_notifications:.4f} segundos por notificação")
        
        # Obter notificações
        get_start_time = time.time()
        notifications = enhanced_context_protocol.get_notifications(limit=100)
        get_end_time = time.time()
        get_elapsed_time = get_end_time - get_start_time
        
        # Verificar se notificações foram recuperadas
        self.assertTrue(notifications["success"])
        self.assertGreaterEqual(len(notifications["notifications"]), num_notifications)
        
        # Imprimir estatísticas
        print(f"Recuperadas {len(notifications['notifications'])} notificações em {get_elapsed_time:.4f} segundos")
    
    def test_06_backup_performance(self):
        """Teste de performance de backup"""
        # Criar backup
        start_time = time.time()
        backup_result = enhanced_context_protocol.create_backup(
            "full",
            "Performance test backup"
        )
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Verificar se backup foi criado
        self.assertTrue(backup_result["success"])
        
        # Imprimir estatísticas
        print(f"Backup criado em {elapsed_time:.2f} segundos")
        print(f"ID do backup: {backup_result['backup_info']['id']}")
        print(f"Arquivos: {backup_result['backup_info']['files_count']}")
        print(f"Tamanho: {backup_result['backup_info']['size_bytes']} bytes")
    
    def test_07_reindexing_performance(self):
        """Teste de performance de reindexação"""
        # Reindexar todos os artefatos
        start_time = time.time()
        reindex_result = enhanced_context_protocol.reindex_all_artifacts()
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Verificar se reindexação foi bem-sucedida
        self.assertTrue(reindex_result["success"])
        
        # Imprimir estatísticas
        print(f"Reindexados {reindex_result['indexed_count']} artefatos em {elapsed_time:.2f} segundos")
        print(f"Média de {elapsed_time/reindex_result['indexed_count']:.4f} segundos por artefato")
    
    def test_08_project_context_performance(self):
        """Teste de performance de contexto de projeto"""
        # Obter contexto do projeto
        start_time = time.time()
        context = enhanced_context_protocol.get_project_context(self.project_id)
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Verificar se contexto foi recuperado
        self.assertIsNotNone(context)
        self.assertIn("project", context)
        self.assertEqual(context["project"]["id"], self.project_id)
        
        # Imprimir estatísticas
        print(f"Contexto do projeto recuperado em {elapsed_time:.2f} segundos")
        print(f"Artefatos no projeto: {len(context['artifacts'])}")
    
    def test_09_system_status(self):
        """Teste de status do sistema após stress tests"""
        # Obter status dos safeguards
        safeguards_status = enhanced_context_protocol.get_safeguards_status()
        
        # Verificar status dos safeguards
        self.assertIsNotNone(safeguards_status)
        
        # Obter status do índice de busca
        search_stats = search_system.get_index_stats()
        
        # Verificar status do índice de busca
        self.assertTrue(search_stats["success"])
        
        # Imprimir estatísticas
        print("Status do sistema após stress tests:")
        print(f"Operações executadas: {safeguards_status.get('operation_count', 'N/A')}")
        print(f"Checkpoints criados: {safeguards_status.get('checkpoint_count', 'N/A')}")
        print(f"Artefatos indexados: {search_stats.get('artifact_count', 'N/A')}")
        print(f"Termos no índice: {search_stats.get('term_count', 'N/A')}")

if __name__ == "__main__":
    unittest.main()
