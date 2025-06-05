#!/usr/bin/env python3
"""
Functional Tests - Continuity Protocol
Testes funcionais para o Continuity Protocol
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

class FunctionalTests(unittest.TestCase):
    """
    Testes funcionais para o Continuity Protocol
    """
    
    @classmethod
    def setUpClass(cls):
        """Configuração inicial para os testes"""
        cls.project_id = f"functional-test-{int(time.time())}"
        cls.project_name = "Functional Test Project"
        cls.project_description = "Project for functional tests"
        
        # Registrar projeto de teste
        cls.project_info = enhanced_context_protocol.register_project(
            cls.project_id,
            cls.project_name,
            cls.project_description
        )
        
        print(f"Projeto de teste criado: {cls.project_id}")
    
    def test_01_project_workflow(self):
        """Teste de fluxo de trabalho de projeto"""
        # Criar múltiplos artefatos
        artifacts = []
        
        # Documento
        doc_content = "# Test Document\n\nThis is a test document for functional tests."
        doc_metadata = {
            "title": "Test Document",
            "description": "Document for functional tests",
            "version": "1.0.0"
        }
        
        doc_info = enhanced_context_protocol.store_artifact(
            doc_content,
            "document",
            self.project_id,
            "functional_tests",
            doc_metadata
        )
        
        artifacts.append(doc_info)
        
        # Código
        code_content = """
def test_function():
    \"\"\"Test function for functional tests\"\"\"
    return "Hello, world!"
"""
        code_metadata = {
            "title": "Test Code",
            "description": "Code for functional tests",
            "language": "python",
            "version": "1.0.0"
        }
        
        code_info = enhanced_context_protocol.store_artifact(
            code_content,
            "code",
            self.project_id,
            "functional_tests",
            code_metadata
        )
        
        artifacts.append(code_info)
        
        # Plano
        plan_content = "# Test Plan\n\n1. Step 1\n2. Step 2\n3. Step 3"
        plan_metadata = {
            "title": "Test Plan",
            "description": "Plan for functional tests",
            "version": "1.0.0"
        }
        
        plan_info = enhanced_context_protocol.store_artifact(
            plan_content,
            "plan",
            self.project_id,
            "functional_tests",
            plan_metadata
        )
        
        artifacts.append(plan_info)
        
        # Verificar se artefatos foram criados
        for artifact in artifacts:
            self.assertIsNotNone(artifact)
            self.assertIn("id", artifact)
            self.assertEqual(artifact["project_id"], self.project_id)
        
        # Obter contexto do projeto
        context = enhanced_context_protocol.get_project_context(self.project_id)
        
        # Verificar contexto do projeto
        self.assertIsNotNone(context)
        self.assertIn("project", context)
        self.assertEqual(context["project"]["id"], self.project_id)
        self.assertIn("artifacts", context)
        self.assertEqual(len(context["artifacts"]), 3)
        
        # Salvar IDs dos artefatos para testes posteriores
        self.__class__.doc_id = doc_info["id"]
        self.__class__.code_id = code_info["id"]
        self.__class__.plan_id = plan_info["id"]
    
    def test_02_versioning_workflow(self):
        """Teste de fluxo de trabalho de versionamento"""
        # Verificar se o ID do documento está disponível
        self.assertTrue(hasattr(self.__class__, "doc_id"), "Document ID not available")
        
        # Obter documento
        doc = enhanced_context_protocol.get_artifact(self.__class__.doc_id)
        
        # Atualizar documento com mudança minor
        updated_content = doc["content"] + "\n\nThis is a minor update."
        
        minor_update = enhanced_context_protocol.update_artifact(
            self.__class__.doc_id,
            updated_content,
            "functional_tests",
            doc.get("metadata", {}),
            "minor",
            "Minor update for testing"
        )
        
        # Verificar se atualização foi bem-sucedida
        self.assertTrue(minor_update["success"])
        self.assertEqual(minor_update["version"], "1.1.0")
        
        # Atualizar documento com mudança major
        doc = enhanced_context_protocol.get_artifact(self.__class__.doc_id)
        major_content = "# Completely Revised Document\n\nThis document has been completely revised."
        
        major_update = enhanced_context_protocol.update_artifact(
            self.__class__.doc_id,
            major_content,
            "functional_tests",
            doc.get("metadata", {}),
            "major",
            "Major update for testing"
        )
        
        # Verificar se atualização foi bem-sucedida
        self.assertTrue(major_update["success"])
        self.assertEqual(major_update["version"], "2.0.0")
        
        # Obter histórico de versões
        history = enhanced_context_protocol.get_artifact_history(self.__class__.doc_id)
        
        # Verificar histórico
        self.assertTrue(history["success"])
        self.assertIn("versions", history)
        self.assertEqual(len(history["versions"]), 3)
        
        # Reverter para versão inicial
        revert = enhanced_context_protocol.revert_artifact(
            self.__class__.doc_id,
            "1.0.0"
        )
        
        # Verificar se reversão foi bem-sucedida
        self.assertTrue(revert["success"])
        
        # Obter documento após reversão
        doc = enhanced_context_protocol.get_artifact(self.__class__.doc_id)
        
        # Verificar se conteúdo foi revertido
        self.assertIn("# Test Document", doc["content"])
        self.assertNotIn("Completely Revised Document", doc["content"])
    
    def test_03_search_workflow(self):
        """Teste de fluxo de trabalho de busca"""
        # Verificar se os IDs dos artefatos estão disponíveis
        self.assertTrue(hasattr(self.__class__, "doc_id"), "Document ID not available")
        self.assertTrue(hasattr(self.__class__, "code_id"), "Code ID not available")
        self.assertTrue(hasattr(self.__class__, "plan_id"), "Plan ID not available")
        
        # Buscar por termo presente em todos os artefatos
        search_result = enhanced_context_protocol.search_artifacts("test")
        
        # Verificar resultado da busca
        self.assertTrue(search_result["success"])
        self.assertIn("results", search_result)
        self.assertGreaterEqual(len(search_result["results"]), 3)
        
        # Buscar por termo presente apenas no código
        code_search = enhanced_context_protocol.search_artifacts("function")
        
        # Verificar resultado da busca
        self.assertTrue(code_search["success"])
        self.assertIn("results", code_search)
        self.assertGreater(len(code_search["results"]), 0)
        
        # Verificar se o artefato de código está nos resultados
        found = False
        for result in code_search["results"]:
            if result["artifact_id"] == self.__class__.code_id:
                found = True
                break
        
        self.assertTrue(found, "Code artifact not found in search results")
        
        # Buscar por metadados
        metadata_search = enhanced_context_protocol.search_by_metadata(
            {"language": "python"}
        )
        
        # Verificar resultado da busca por metadados
        self.assertTrue(metadata_search["success"])
        self.assertIn("results", metadata_search)
        self.assertGreater(len(metadata_search["results"]), 0)
        
        # Verificar se o artefato de código está nos resultados
        found = False
        for result in metadata_search["results"]:
            if result["artifact_id"] == self.__class__.code_id:
                found = True
                break
        
        self.assertTrue(found, "Code artifact not found in metadata search results")
    
    def test_04_notification_workflow(self):
        """Teste de fluxo de trabalho de notificações"""
        # Criar várias notificações
        notifications = []
        
        # Notificação de informação
        info_notification = enhanced_context_protocol.create_notification(
            "Info Notification",
            "This is an info notification for functional tests",
            "info",
            "functional_tests",
            {"project_id": self.project_id}
        )
        
        notifications.append(info_notification["notification_info"]["id"])
        
        # Notificação de aviso
        warning_notification = enhanced_context_protocol.create_notification(
            "Warning Notification",
            "This is a warning notification for functional tests",
            "warning",
            "functional_tests",
            {"project_id": self.project_id}
        )
        
        notifications.append(warning_notification["notification_info"]["id"])
        
        # Notificação de erro
        error_notification = enhanced_context_protocol.create_notification(
            "Error Notification",
            "This is an error notification for functional tests",
            "error",
            "functional_tests",
            {"project_id": self.project_id}
        )
        
        notifications.append(error_notification["notification_info"]["id"])
        
        # Obter notificações não lidas
        unread = enhanced_context_protocol.get_notifications(unread_only=True)
        
        # Verificar notificações não lidas
        self.assertTrue(unread["success"])
        self.assertIn("notifications", unread)
        self.assertGreaterEqual(len(unread["notifications"]), 3)
        
        # Marcar uma notificação como lida
        mark_result = enhanced_context_protocol.mark_notification_as_read(notifications[0])
        
        # Verificar se notificação foi marcada como lida
        self.assertTrue(mark_result["success"])
        
        # Obter notificações não lidas novamente
        unread_after = enhanced_context_protocol.get_notifications(unread_only=True)
        
        # Verificar se número de notificações não lidas diminuiu
        self.assertTrue(unread_after["success"])
        self.assertIn("notifications", unread_after)
        self.assertLess(len(unread_after["notifications"]), len(unread["notifications"]))
    
    def test_05_backup_workflow(self):
        """Teste de fluxo de trabalho de backup"""
        # Criar backup completo
        full_backup = enhanced_context_protocol.create_backup(
            "full",
            "Full backup for functional tests"
        )
        
        # Verificar se backup foi criado
        self.assertTrue(full_backup["success"])
        self.assertIn("backup_info", full_backup)
        
        # Salvar ID do backup para testes posteriores
        full_backup_id = full_backup["backup_info"]["id"]
        
        # Criar backup incremental
        incremental_backup = enhanced_context_protocol.create_backup(
            "incremental",
            "Incremental backup for functional tests"
        )
        
        # Verificar se backup foi criado
        self.assertTrue(incremental_backup["success"])
        self.assertIn("backup_info", incremental_backup)
        
        # Obter lista de backups
        backups = backup_system.get_backups_list()
        
        # Verificar lista de backups
        self.assertTrue(backups["success"])
        self.assertIn("backups", backups)
        self.assertGreaterEqual(len(backups["backups"]), 2)
        
        # Verificar se os backups criados estão na lista
        found_full = False
        found_incremental = False
        
        for backup in backups["backups"]:
            if backup["id"] == full_backup_id:
                found_full = True
            elif backup["id"] == incremental_backup["backup_info"]["id"]:
                found_incremental = True
        
        self.assertTrue(found_full, "Full backup not found in backups list")
        self.assertTrue(found_incremental, "Incremental backup not found in backups list")
    
    def test_06_cross_functional_workflow(self):
        """Teste de fluxo de trabalho entre funcionalidades"""
        # Verificar se o ID do documento está disponível
        self.assertTrue(hasattr(self.__class__, "doc_id"), "Document ID not available")
        
        # Obter documento
        doc = enhanced_context_protocol.get_artifact(self.__class__.doc_id)
        
        # Atualizar documento
        updated_content = doc["content"] + "\n\nThis update will trigger multiple systems."
        
        update_result = enhanced_context_protocol.update_artifact(
            self.__class__.doc_id,
            updated_content,
            "functional_tests",
            doc.get("metadata", {}),
            "minor",
            "Update for cross-functional test"
        )
        
        # Verificar se atualização foi bem-sucedida
        self.assertTrue(update_result["success"])
        
        # Verificar se versão foi criada
        version_result = enhanced_context_protocol.get_artifact_version(
            self.__class__.doc_id,
            update_result["version"]
        )
        
        self.assertTrue(version_result["success"])
        self.assertIn("content", version_result)
        self.assertIn("This update will trigger multiple systems.", version_result["content"])
        
        # Verificar se documento pode ser encontrado na busca
        search_result = enhanced_context_protocol.search_artifacts("trigger multiple systems")
        
        self.assertTrue(search_result["success"])
        self.assertIn("results", search_result)
        self.assertGreater(len(search_result["results"]), 0)
        
        # Verificar se notificação foi criada
        notifications = enhanced_context_protocol.get_notifications(limit=5)
        
        self.assertTrue(notifications["success"])
        self.assertIn("notifications", notifications)
        
        # Criar backup após todas as operações
        backup_result = enhanced_context_protocol.create_backup(
            "full",
            "Backup after cross-functional test"
        )
        
        self.assertTrue(backup_result["success"])
    
    def test_07_stress_test(self):
        """Teste de stress"""
        # Criar múltiplos artefatos em sequência
        num_artifacts = 10
        artifacts = []
        
        for i in range(num_artifacts):
            content = f"# Stress Test Artifact {i}\n\nThis is artifact {i} for stress testing."
            metadata = {
                "title": f"Stress Test {i}",
                "description": f"Artifact {i} for stress testing",
                "version": "1.0.0",
                "stress_index": i
            }
            
            artifact_info = enhanced_context_protocol.store_artifact(
                content,
                "document",
                self.project_id,
                "functional_tests",
                metadata
            )
            
            artifacts.append(artifact_info)
            
            # Verificar se artefato foi criado
            self.assertIsNotNone(artifact_info)
            self.assertIn("id", artifact_info)
        
        # Verificar se todos os artefatos foram criados
        self.assertEqual(len(artifacts), num_artifacts)
        
        # Obter contexto do projeto
        context = enhanced_context_protocol.get_project_context(self.project_id)
        
        # Verificar se todos os artefatos estão no contexto
        self.assertGreaterEqual(len(context["artifacts"]), num_artifacts)
        
        # Buscar por termo presente em todos os artefatos de stress
        search_result = enhanced_context_protocol.search_artifacts("stress testing")
        
        # Verificar resultado da busca
        self.assertTrue(search_result["success"])
        self.assertIn("results", search_result)
        self.assertGreaterEqual(len(search_result["results"]), num_artifacts)
    
    def test_08_error_handling(self):
        """Teste de tratamento de erros"""
        # Tentar obter artefato inexistente
        invalid_artifact = enhanced_context_protocol.get_artifact("non_existent_artifact_id")
        
        # Verificar se retornou None
        self.assertIsNone(invalid_artifact)
        
        # Tentar obter versão de artefato inexistente
        invalid_version = enhanced_context_protocol.get_artifact_version("non_existent_artifact_id")
        
        # Verificar se retornou erro
        self.assertFalse(invalid_version["success"])
        
        # Tentar obter contexto de projeto inexistente
        invalid_context = enhanced_context_protocol.get_project_context("non_existent_project_id")
        
        # Verificar se retornou erro ou objeto vazio
        if isinstance(invalid_context, dict) and "error" in invalid_context:
            self.assertIn("error", invalid_context)
        else:
            self.assertIn("project", invalid_context)
            self.assertEqual(len(invalid_context["artifacts"]), 0)
    
    def test_09_cleanup(self):
        """Teste de limpeza"""
        # Criar backup final
        backup_result = enhanced_context_protocol.create_backup(
            "full",
            "Final backup for functional tests"
        )
        
        # Verificar se backup foi criado
        self.assertTrue(backup_result["success"])
        
        # Reindexar todos os artefatos
        reindex_result = enhanced_context_protocol.reindex_all_artifacts()
        
        # Verificar se reindexação foi bem-sucedida
        self.assertTrue(reindex_result["success"])
        
        # Criar notificação de conclusão
        notification_result = enhanced_context_protocol.create_notification(
            "Functional Tests Completed",
            "All functional tests have been completed successfully",
            "success",
            "functional_tests",
            {"project_id": self.project_id}
        )
        
        # Verificar se notificação foi criada
        self.assertTrue(notification_result["success"])

if __name__ == "__main__":
    unittest.main()
