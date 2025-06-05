#!/usr/bin/env python3
"""
Validation Tests - Continuity Protocol
Testes de validação para o Continuity Protocol
"""

import os
import sys
import json
import time
import unittest
import subprocess
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

class ValidationTests(unittest.TestCase):
    """
    Testes de validação para o Continuity Protocol
    """
    
    @classmethod
    def setUpClass(cls):
        """Configuração inicial para os testes"""
        cls.project_id = f"validation-test-{int(time.time())}"
        cls.project_name = "Validation Test Project"
        cls.project_description = "Project for validation tests"
        
        # Registrar projeto de teste
        cls.project_info = enhanced_context_protocol.register_project(
            cls.project_id,
            cls.project_name,
            cls.project_description
        )
        
        print(f"Projeto de teste criado: {cls.project_id}")
    
    def test_01_unified_functionality(self):
        """Teste de unificação funcional entre Amazon Q CLI e Claude Desktop"""
        # Criar artefato para Amazon Q CLI
        amazon_q_content = "# Amazon Q CLI Test\n\nThis artifact was created for testing unified functionality."
        amazon_q_metadata = {
            "title": "Amazon Q CLI Test",
            "description": "Artifact for testing unified functionality",
            "version": "1.0.0",
            "agent": "amazon_q_cli"
        }
        
        amazon_q_artifact = enhanced_context_protocol.store_artifact(
            amazon_q_content,
            "document",
            self.project_id,
            "amazon_q_cli",
            amazon_q_metadata
        )
        
        # Verificar se artefato foi criado
        self.assertIsNotNone(amazon_q_artifact)
        self.assertIn("id", amazon_q_artifact)
        
        # Criar artefato para Claude Desktop
        claude_content = "# Claude Desktop Test\n\nThis artifact was created for testing unified functionality."
        claude_metadata = {
            "title": "Claude Desktop Test",
            "description": "Artifact for testing unified functionality",
            "version": "1.0.0",
            "agent": "claude_desktop"
        }
        
        claude_artifact = enhanced_context_protocol.store_artifact(
            claude_content,
            "document",
            self.project_id,
            "claude_desktop",
            claude_metadata
        )
        
        # Verificar se artefato foi criado
        self.assertIsNotNone(claude_artifact)
        self.assertIn("id", claude_artifact)
        
        # Obter contexto do projeto
        context = enhanced_context_protocol.get_project_context(self.project_id)
        
        # Verificar se ambos os artefatos estão no contexto
        self.assertIsNotNone(context)
        self.assertIn("artifacts", context)
        self.assertEqual(len(context["artifacts"]), 2)
        
        # Verificar se os artefatos podem ser acessados individualmente
        amazon_q_result = enhanced_context_protocol.get_artifact(amazon_q_artifact["id"])
        claude_result = enhanced_context_protocol.get_artifact(claude_artifact["id"])
        
        self.assertIsNotNone(amazon_q_result)
        self.assertIsNotNone(claude_result)
        
        # Salvar IDs dos artefatos para testes posteriores
        self.__class__.amazon_q_artifact_id = amazon_q_artifact["id"]
        self.__class__.claude_artifact_id = claude_artifact["id"]
    
    def test_02_cross_agent_interaction(self):
        """Teste de interação entre agentes"""
        # Verificar se os IDs dos artefatos estão disponíveis
        self.assertTrue(hasattr(self.__class__, "amazon_q_artifact_id"), "Amazon Q artifact ID not available")
        self.assertTrue(hasattr(self.__class__, "claude_artifact_id"), "Claude artifact ID not available")
        
        # Amazon Q CLI atualiza artefato do Claude Desktop
        claude_artifact = enhanced_context_protocol.get_artifact(self.__class__.claude_artifact_id)
        updated_content = claude_artifact["content"] + "\n\nThis update was made by Amazon Q CLI."
        
        update_result = enhanced_context_protocol.update_artifact(
            self.__class__.claude_artifact_id,
            updated_content,
            "amazon_q_cli",
            claude_artifact.get("metadata", {}),
            "minor",
            "Update by Amazon Q CLI"
        )
        
        # Verificar se atualização foi bem-sucedida
        self.assertTrue(update_result["success"])
        
        # Claude Desktop atualiza artefato do Amazon Q CLI
        amazon_q_artifact = enhanced_context_protocol.get_artifact(self.__class__.amazon_q_artifact_id)
        updated_content = amazon_q_artifact["content"] + "\n\nThis update was made by Claude Desktop."
        
        update_result = enhanced_context_protocol.update_artifact(
            self.__class__.amazon_q_artifact_id,
            updated_content,
            "claude_desktop",
            amazon_q_artifact.get("metadata", {}),
            "minor",
            "Update by Claude Desktop"
        )
        
        # Verificar se atualização foi bem-sucedida
        self.assertTrue(update_result["success"])
        
        # Verificar se as atualizações foram aplicadas
        claude_artifact = enhanced_context_protocol.get_artifact(self.__class__.claude_artifact_id)
        amazon_q_artifact = enhanced_context_protocol.get_artifact(self.__class__.amazon_q_artifact_id)
        
        self.assertIn("This update was made by Amazon Q CLI", claude_artifact["content"])
        self.assertIn("This update was made by Claude Desktop", amazon_q_artifact["content"])
    
    def test_03_versioning_validation(self):
        """Teste de validação de versionamento"""
        # Verificar se os IDs dos artefatos estão disponíveis
        self.assertTrue(hasattr(self.__class__, "amazon_q_artifact_id"), "Amazon Q artifact ID not available")
        
        # Obter histórico de versões
        history_result = enhanced_context_protocol.get_artifact_history(self.__class__.amazon_q_artifact_id)
        
        # Verificar histórico
        self.assertTrue(history_result["success"])
        self.assertIn("versions", history_result)
        self.assertEqual(len(history_result["versions"]), 2)
        
        # Verificar se as versões têm os criadores corretos
        versions = history_result["versions"]
        
        # A primeira versão deve ser do Amazon Q CLI
        self.assertEqual(versions[0]["created_by"], "amazon_q_cli")
        
        # A segunda versão deve ser do Claude Desktop
        self.assertEqual(versions[1]["created_by"], "claude_desktop")
        
        # Comparar versões
        compare_result = enhanced_context_protocol.compare_artifact_versions(
            self.__class__.amazon_q_artifact_id,
            "1.0.0",
            "1.1.0"
        )
        
        # Verificar comparação
        self.assertTrue(compare_result["success"])
        self.assertIn("diff", compare_result)
        self.assertIn("+This update was made by Claude Desktop", compare_result["diff"])
    
    def test_04_search_validation(self):
        """Teste de validação de busca"""
        # Buscar por termo presente em ambos os artefatos
        search_result = enhanced_context_protocol.search_artifacts("unified functionality")
        
        # Verificar resultado da busca
        self.assertTrue(search_result["success"])
        self.assertIn("results", search_result)
        self.assertEqual(len(search_result["results"]), 2)
        
        # Buscar por termo presente apenas no artefato do Amazon Q CLI
        amazon_q_search = enhanced_context_protocol.search_artifacts("Amazon Q CLI")
        
        # Verificar resultado da busca
        self.assertTrue(amazon_q_search["success"])
        self.assertIn("results", amazon_q_search)
        self.assertEqual(len(amazon_q_search["results"]), 1)
        
        # Buscar por termo presente apenas no artefato do Claude Desktop
        claude_search = enhanced_context_protocol.search_artifacts("Claude Desktop")
        
        # Verificar resultado da busca
        self.assertTrue(claude_search["success"])
        self.assertIn("results", claude_search)
        self.assertEqual(len(claude_search["results"]), 1)
        
        # Buscar por metadados
        amazon_q_metadata_search = enhanced_context_protocol.search_by_metadata(
            {"agent": "amazon_q_cli"}
        )
        
        # Verificar resultado da busca por metadados
        self.assertTrue(amazon_q_metadata_search["success"])
        self.assertIn("results", amazon_q_metadata_search)
        self.assertEqual(len(amazon_q_metadata_search["results"]), 1)
    
    def test_05_notification_validation(self):
        """Teste de validação de notificações"""
        # Criar notificação para Amazon Q CLI
        amazon_q_notification = enhanced_context_protocol.create_notification(
            "Amazon Q CLI Notification",
            "This notification is for Amazon Q CLI",
            "info",
            "amazon_q_cli",
            {"agent": "amazon_q_cli"}
        )
        
        # Verificar se notificação foi criada
        self.assertTrue(amazon_q_notification["success"])
        
        # Criar notificação para Claude Desktop
        claude_notification = enhanced_context_protocol.create_notification(
            "Claude Desktop Notification",
            "This notification is for Claude Desktop",
            "info",
            "claude_desktop",
            {"agent": "claude_desktop"}
        )
        
        # Verificar se notificação foi criada
        self.assertTrue(claude_notification["success"])
        
        # Obter notificações
        notifications = enhanced_context_protocol.get_notifications(limit=10)
        
        # Verificar se notificações foram recuperadas
        self.assertTrue(notifications["success"])
        self.assertIn("notifications", notifications)
        self.assertGreaterEqual(len(notifications["notifications"]), 2)
        
        # Verificar se ambas as notificações estão presentes
        found_amazon_q = False
        found_claude = False
        
        for notification in notifications["notifications"]:
            if notification["title"] == "Amazon Q CLI Notification":
                found_amazon_q = True
            elif notification["title"] == "Claude Desktop Notification":
                found_claude = True
        
        self.assertTrue(found_amazon_q, "Amazon Q CLI notification not found")
        self.assertTrue(found_claude, "Claude Desktop notification not found")
    
    def test_06_backup_validation(self):
        """Teste de validação de backup"""
        # Criar backup
        backup_result = enhanced_context_protocol.create_backup(
            "full",
            "Validation test backup"
        )
        
        # Verificar se backup foi criado
        self.assertTrue(backup_result["success"])
        self.assertIn("backup_info", backup_result)
        
        # Obter lista de backups
        backups = backup_system.get_backups_list()
        
        # Verificar se lista de backups foi recuperada
        self.assertTrue(backups["success"])
        self.assertIn("backups", backups)
        self.assertGreater(len(backups["backups"]), 0)
        
        # Verificar se o backup criado está na lista
        found = False
        for backup in backups["backups"]:
            if backup["id"] == backup_result["backup_info"]["id"]:
                found = True
                break
        
        self.assertTrue(found, "Backup not found in backups list")
    
    def test_07_server_restart_validation(self):
        """Teste de validação após reinício do servidor"""
        # Criar artefato antes do reinício
        pre_restart_content = "# Pre-Restart Test\n\nThis artifact was created before server restart."
        pre_restart_metadata = {
            "title": "Pre-Restart Test",
            "description": "Artifact created before server restart",
            "version": "1.0.0"
        }
        
        pre_restart_artifact = enhanced_context_protocol.store_artifact(
            pre_restart_content,
            "document",
            self.project_id,
            "validation_tests",
            pre_restart_metadata
        )
        
        # Verificar se artefato foi criado
        self.assertIsNotNone(pre_restart_artifact)
        self.assertIn("id", pre_restart_artifact)
        
        # Salvar ID do artefato
        pre_restart_id = pre_restart_artifact["id"]
        
        # Simular reinício do servidor (não reinicia realmente, apenas valida persistência)
        print("Simulando reinício do servidor...")
        time.sleep(2)  # Pequena pausa para simular reinício
        
        # Verificar se artefato ainda está acessível após "reinício"
        post_restart_artifact = enhanced_context_protocol.get_artifact(pre_restart_id)
        
        # Verificar se artefato foi recuperado
        self.assertIsNotNone(post_restart_artifact)
        self.assertEqual(post_restart_artifact["id"], pre_restart_id)
        self.assertEqual(post_restart_artifact["content"], pre_restart_content)
    
    def test_08_system_validation(self):
        """Teste de validação do sistema"""
        # Obter status dos safeguards
        safeguards_status = enhanced_context_protocol.get_safeguards_status()
        
        # Verificar status dos safeguards
        self.assertIsNotNone(safeguards_status)
        self.assertIn("max_lines_per_operation", safeguards_status)
        
        # Obter status do índice de busca
        search_stats = search_system.get_index_stats()
        
        # Verificar status do índice de busca
        self.assertTrue(search_stats["success"])
        self.assertIn("artifact_count", search_stats)
        
        # Verificar se o número de artefatos indexados corresponde ao número de artefatos no projeto
        context = enhanced_context_protocol.get_project_context(self.project_id)
        self.assertGreaterEqual(search_stats["artifact_count"], len(context["artifacts"]))
    
    def test_09_cross_platform_validation(self):
        """Teste de validação entre plataformas"""
        # Este teste verifica se o sistema funciona em diferentes plataformas
        # Como não podemos realmente testar em diferentes plataformas em um único teste,
        # vamos verificar se o sistema detecta corretamente a plataforma atual
        
        # Obter informações do sistema
        system_info = {
            "platform": sys.platform,
            "python_version": sys.version,
            "os_name": os.name
        }
        
        # Imprimir informações do sistema
        print(f"Plataforma: {system_info['platform']}")
        print(f"Versão do Python: {system_info['python_version']}")
        print(f"Nome do SO: {system_info['os_name']}")
        
        # Verificar se o sistema está rodando em uma plataforma suportada
        supported_platforms = ["linux", "darwin", "win32"]
        self.assertIn(system_info["platform"], supported_platforms, 
                     f"Plataforma {system_info['platform']} não suportada")
    
    def test_10_final_validation(self):
        """Teste de validação final"""
        # Criar artefato de validação final
        final_content = "# Validation Complete\n\nAll validation tests have been completed successfully."
        final_metadata = {
            "title": "Validation Complete",
            "description": "Final validation artifact",
            "version": "1.0.0",
            "status": "validated"
        }
        
        final_artifact = enhanced_context_protocol.store_artifact(
            final_content,
            "validation",
            self.project_id,
            "validation_tests",
            final_metadata
        )
        
        # Verificar se artefato foi criado
        self.assertIsNotNone(final_artifact)
        self.assertIn("id", final_artifact)
        
        # Criar notificação de validação concluída
        notification_result = enhanced_context_protocol.create_notification(
            "Validation Complete",
            "All validation tests have been completed successfully",
            "success",
            "validation_tests",
            {"project_id": self.project_id, "status": "validated"}
        )
        
        # Verificar se notificação foi criada
        self.assertTrue(notification_result["success"])
        
        # Criar backup final
        backup_result = enhanced_context_protocol.create_backup(
            "full",
            "Final validation backup"
        )
        
        # Verificar se backup foi criado
        self.assertTrue(backup_result["success"])

if __name__ == "__main__":
    unittest.main()
