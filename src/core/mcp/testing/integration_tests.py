#!/usr/bin/env python3
"""
Integration Tests - Continuity Protocol
Testes de integração para o Continuity Protocol
"""

import os
import sys
import json
import time
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

class IntegrationTests(unittest.TestCase):
    """
    Testes de integração para o Continuity Protocol
    """
    
    @classmethod
    def setUpClass(cls):
        """Configuração inicial para os testes"""
        cls.project_id = f"test-project-{int(time.time())}"
        cls.project_name = "Test Project"
        cls.project_description = "Project for integration tests"
        
        # Registrar projeto de teste
        cls.project_info = enhanced_context_protocol.register_project(
            cls.project_id,
            cls.project_name,
            cls.project_description
        )
        
        print(f"Projeto de teste criado: {cls.project_id}")
    
    @classmethod
    def tearDownClass(cls):
        """Limpeza após os testes"""
        # Criar backup dos artefatos de teste
        backup_result = backup_system.create_backup(
            "test",
            f"Backup de artefatos de teste - {cls.project_id}"
        )
        
        print(f"Backup de artefatos de teste criado: {backup_result.get('backup_info', {}).get('id', 'unknown')}")
    
    def test_01_artifact_creation(self):
        """Teste de criação de artefato"""
        # Criar artefato
        content = "# Test Artifact\n\nThis is a test artifact for integration tests."
        artifact_type = "document"
        metadata = {
            "title": "Test Artifact",
            "description": "Artifact for integration tests",
            "version": "1.0.0"
        }
        
        artifact_info = enhanced_context_protocol.store_artifact(
            content,
            artifact_type,
            self.project_id,
            "integration_tests",
            metadata
        )
        
        # Verificar se artefato foi criado
        self.assertIsNotNone(artifact_info)
        self.assertIn("id", artifact_info)
        self.assertEqual(artifact_info["type"], artifact_type)
        self.assertEqual(artifact_info["project_id"], self.project_id)
        
        # Salvar ID do artefato para testes posteriores
        self.__class__.artifact_id = artifact_info["id"]
        print(f"Artefato de teste criado: {self.__class__.artifact_id}")
    
    def test_02_artifact_retrieval(self):
        """Teste de recuperação de artefato"""
        # Verificar se o ID do artefato está disponível
        self.assertTrue(hasattr(self.__class__, "artifact_id"), "Artifact ID not available")
        
        # Recuperar artefato
        artifact = enhanced_context_protocol.get_artifact(self.__class__.artifact_id)
        
        # Verificar se artefato foi recuperado
        self.assertIsNotNone(artifact)
        self.assertEqual(artifact["id"], self.__class__.artifact_id)
        self.assertIn("content", artifact)
        self.assertIn("# Test Artifact", artifact["content"])
    
    def test_03_versioning(self):
        """Teste de versionamento"""
        # Verificar se o ID do artefato está disponível
        self.assertTrue(hasattr(self.__class__, "artifact_id"), "Artifact ID not available")
        
        # Obter versão atual
        version_result = enhanced_context_protocol.get_artifact_version(self.__class__.artifact_id)
        
        # Verificar se versão foi recuperada
        self.assertTrue(version_result["success"])
        self.assertIn("version_info", version_result)
        self.assertEqual(version_result["version_info"]["version"], "1.0.0")
        
        # Atualizar artefato
        artifact = enhanced_context_protocol.get_artifact(self.__class__.artifact_id)
        updated_content = artifact["content"] + "\n\nThis content was updated."
        
        update_result = enhanced_context_protocol.update_artifact(
            self.__class__.artifact_id,
            updated_content,
            "integration_tests",
            artifact.get("metadata", {}),
            "minor",
            "Updated content for testing"
        )
        
        # Verificar se atualização foi bem-sucedida
        self.assertTrue(update_result["success"])
        self.assertEqual(update_result["version"], "1.1.0")
        
        # Obter histórico de versões
        history_result = enhanced_context_protocol.get_artifact_history(self.__class__.artifact_id)
        
        # Verificar histórico
        self.assertTrue(history_result["success"])
        self.assertIn("versions", history_result)
        self.assertEqual(len(history_result["versions"]), 2)
        
        # Comparar versões
        compare_result = enhanced_context_protocol.compare_artifact_versions(
            self.__class__.artifact_id,
            "1.0.0",
            "1.1.0"
        )
        
        # Verificar comparação
        self.assertTrue(compare_result["success"])
        self.assertIn("diff", compare_result)
        self.assertIn("+This content was updated.", compare_result["diff"])
    
    def test_04_search(self):
        """Teste de busca"""
        # Verificar se o ID do artefato está disponível
        self.assertTrue(hasattr(self.__class__, "artifact_id"), "Artifact ID not available")
        
        # Buscar por termo
        search_result = enhanced_context_protocol.search_artifacts("test artifact")
        
        # Verificar resultado da busca
        self.assertTrue(search_result["success"])
        self.assertIn("results", search_result)
        self.assertGreater(len(search_result["results"]), 0)
        
        # Verificar se o artefato de teste está nos resultados
        found = False
        for result in search_result["results"]:
            if result["artifact_id"] == self.__class__.artifact_id:
                found = True
                break
        
        self.assertTrue(found, "Artifact not found in search results")
        
        # Buscar por metadados
        metadata_search_result = enhanced_context_protocol.search_by_metadata(
            {"title": "Test Artifact"}
        )
        
        # Verificar resultado da busca por metadados
        self.assertTrue(metadata_search_result["success"])
        self.assertIn("results", metadata_search_result)
        self.assertGreater(len(metadata_search_result["results"]), 0)
    
    def test_05_notifications(self):
        """Teste de notificações"""
        # Criar notificação
        notification_result = enhanced_context_protocol.create_notification(
            "Test Notification",
            "This is a test notification for integration tests",
            "info",
            "integration_tests",
            {"artifact_id": getattr(self.__class__, "artifact_id", "unknown")}
        )
        
        # Verificar se notificação foi criada
        self.assertTrue(notification_result["success"])
        self.assertIn("notification_info", notification_result)
        
        # Salvar ID da notificação para testes posteriores
        self.__class__.notification_id = notification_result["notification_info"]["id"]
        
        # Obter notificações
        notifications_result = enhanced_context_protocol.get_notifications(limit=10)
        
        # Verificar se notificações foram recuperadas
        self.assertTrue(notifications_result["success"])
        self.assertIn("notifications", notifications_result)
        self.assertGreater(len(notifications_result["notifications"]), 0)
        
        # Marcar notificação como lida
        mark_result = enhanced_context_protocol.mark_notification_as_read(self.__class__.notification_id)
        
        # Verificar se notificação foi marcada como lida
        self.assertTrue(mark_result["success"])
    
    def test_06_backup(self):
        """Teste de backup"""
        # Criar backup
        backup_result = enhanced_context_protocol.create_backup(
            "full",
            "Backup for integration tests"
        )
        
        # Verificar se backup foi criado
        self.assertTrue(backup_result["success"])
        self.assertIn("backup_info", backup_result)
        
        # Salvar ID do backup para testes posteriores
        self.__class__.backup_id = backup_result["backup_info"]["id"]
        
        # Obter lista de backups
        backups_result = backup_system.get_backups_list()
        
        # Verificar se lista de backups foi recuperada
        self.assertTrue(backups_result["success"])
        self.assertIn("backups", backups_result)
        self.assertGreater(len(backups_result["backups"]), 0)
    
    def test_07_revert_version(self):
        """Teste de reversão de versão"""
        # Verificar se o ID do artefato está disponível
        self.assertTrue(hasattr(self.__class__, "artifact_id"), "Artifact ID not available")
        
        # Reverter para versão anterior
        revert_result = enhanced_context_protocol.revert_artifact(
            self.__class__.artifact_id,
            "1.0.0"
        )
        
        # Verificar se reversão foi bem-sucedida
        self.assertTrue(revert_result["success"])
        self.assertIn("version_info", revert_result)
        self.assertEqual(revert_result["version_info"]["version"], "1.2.0")
        
        # Obter conteúdo atual
        artifact = enhanced_context_protocol.get_artifact(self.__class__.artifact_id)
        
        # Verificar se conteúdo foi revertido
        self.assertNotIn("This content was updated.", artifact["content"])
    
    def test_08_system_status(self):
        """Teste de status do sistema"""
        # Obter status dos safeguards
        safeguards_status = enhanced_context_protocol.get_safeguards_status()
        
        # Verificar status dos safeguards
        self.assertIsNotNone(safeguards_status)
        self.assertIn("max_lines_per_operation", safeguards_status)
        self.assertIn("max_session_minutes", safeguards_status)
        
        # Obter status do índice de busca
        search_stats = search_system.get_index_stats()
        
        # Verificar status do índice de busca
        self.assertTrue(search_stats["success"])
        self.assertIn("artifact_count", search_stats)
        self.assertIn("term_count", search_stats)
    
    def test_09_project_context(self):
        """Teste de contexto do projeto"""
        # Obter contexto do projeto
        context = enhanced_context_protocol.get_project_context(self.project_id)
        
        # Verificar contexto do projeto
        self.assertIsNotNone(context)
        self.assertIn("project", context)
        self.assertEqual(context["project"]["id"], self.project_id)
        self.assertIn("artifacts", context)
        self.assertGreater(len(context["artifacts"]), 0)
    
    def test_10_reindex_all(self):
        """Teste de reindexação"""
        # Reindexar todos os artefatos
        reindex_result = enhanced_context_protocol.reindex_all_artifacts()
        
        # Verificar se reindexação foi bem-sucedida
        self.assertTrue(reindex_result["success"])
        self.assertIn("indexed_count", reindex_result)
        self.assertGreater(reindex_result["indexed_count"], 0)

if __name__ == "__main__":
    unittest.main()
