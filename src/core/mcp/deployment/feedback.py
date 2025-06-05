#!/usr/bin/env python3
"""
Feedback System - Continuity Protocol
Sistema de feedback para otimização do Continuity Protocol
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Callable

# Adicionar diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Importar componentes
try:
    from core.mcp.notification import notification_system
except ImportError:
    print("Erro ao importar componentes do Continuity Protocol")
    sys.exit(1)

class FeedbackSystem:
    """
    Sistema de feedback para otimização do Continuity Protocol
    """
    
    def __init__(self, feedback_dir: str = None):
        """
        Inicializa o sistema de feedback
        
        Args:
            feedback_dir: Diretório para armazenamento de feedback
        """
        # Configurar diretório de feedback
        if feedback_dir:
            self.feedback_dir = feedback_dir
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            self.feedback_dir = os.path.join(base_dir, "feedback")
        
        # Criar diretório se não existir
        os.makedirs(self.feedback_dir, exist_ok=True)
        
        # Arquivo de feedback
        self.feedback_file = os.path.join(self.feedback_dir, "feedback.json")
        
        # Arquivo de sugestões
        self.suggestions_file = os.path.join(self.feedback_dir, "suggestions.json")
        
        # Carregar ou criar feedback
        self.feedback = self._load_or_create_feedback()
        
        # Carregar ou criar sugestões
        self.suggestions = self._load_or_create_suggestions()
        
        # Callbacks para feedback
        self.feedback_callbacks = {}
    
    def _load_or_create_feedback(self) -> Dict[str, Any]:
        """
        Carrega ou cria feedback
        
        Returns:
            Dict: Feedback
        """
        if os.path.exists(self.feedback_file):
            try:
                with open(self.feedback_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Criar feedback padrão
        feedback = {
            "feedback": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Salvar feedback
        with open(self.feedback_file, 'w') as f:
            json.dump(feedback, f, indent=2)
        
        return feedback
    
    def _load_or_create_suggestions(self) -> Dict[str, Any]:
        """
        Carrega ou cria sugestões
        
        Returns:
            Dict: Sugestões
        """
        if os.path.exists(self.suggestions_file):
            try:
                with open(self.suggestions_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Criar sugestões padrão
        suggestions = {
            "suggestions": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Salvar sugestões
        with open(self.suggestions_file, 'w') as f:
            json.dump(suggestions, f, indent=2)
        
        return suggestions
    
    def _save_feedback(self) -> None:
        """Salva feedback"""
        self.feedback["updated_at"] = datetime.now().isoformat()
        with open(self.feedback_file, 'w') as f:
            json.dump(self.feedback, f, indent=2)
    
    def _save_suggestions(self) -> None:
        """Salva sugestões"""
        self.suggestions["updated_at"] = datetime.now().isoformat()
        with open(self.suggestions_file, 'w') as f:
            json.dump(self.suggestions, f, indent=2)
    
    def submit_feedback(self, category: str, rating: int, comment: str = None,
                       user_id: str = None, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Submete feedback
        
        Args:
            category: Categoria do feedback (e.g., "usability", "performance", "feature")
            rating: Avaliação (1-5)
            comment: Comentário
            user_id: ID do usuário
            metadata: Metadados adicionais
            
        Returns:
            Dict: Informações do feedback
        """
        # Validar categoria
        valid_categories = ["usability", "performance", "feature", "bug", "documentation", "other"]
        if category not in valid_categories:
            return {
                "success": False,
                "error": f"Categoria inválida. Categorias válidas: {', '.join(valid_categories)}"
            }
        
        # Validar avaliação
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return {
                "success": False,
                "error": "Avaliação deve ser um número inteiro entre 1 e 5"
            }
        
        # Criar feedback
        feedback_info = {
            "id": f"feedback_{int(time.time())}_{category}",
            "category": category,
            "rating": rating,
            "comment": comment,
            "user_id": user_id,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "status": "new"
        }
        
        # Adicionar feedback
        self.feedback["feedback"].append(feedback_info)
        self._save_feedback()
        
        # Executar callbacks
        self._execute_feedback_callbacks(feedback_info)
        
        # Notificar sobre novo feedback
        notification_system.create_notification(
            f"Novo feedback: {category}",
            f"Novo feedback recebido na categoria {category} com avaliação {rating}/5",
            "info",
            "feedback",
            {
                "category": category,
                "rating": rating,
                "feedback_id": feedback_info["id"]
            }
        )
        
        # Gerar sugestão automática se avaliação for baixa
        if rating <= 2:
            self._generate_suggestion(feedback_info)
        
        return {
            "success": True,
            "feedback": feedback_info
        }
    
    def _generate_suggestion(self, feedback_info: Dict[str, Any]) -> None:
        """
        Gera sugestão automática com base em feedback
        
        Args:
            feedback_info: Informações do feedback
        """
        category = feedback_info["category"]
        rating = feedback_info["rating"]
        comment = feedback_info["comment"]
        
        # Determinar área de melhoria com base na categoria
        improvement_area = {
            "usability": "interface do usuário",
            "performance": "performance do sistema",
            "feature": "funcionalidades",
            "bug": "correção de bugs",
            "documentation": "documentação",
            "other": "aspectos gerais"
        }.get(category, "aspectos gerais")
        
        # Gerar sugestão
        suggestion_text = f"Melhorar a {improvement_area} com base em feedback negativo (avaliação {rating}/5)"
        
        if comment:
            suggestion_text += f": \"{comment}\""
        
        # Criar sugestão
        suggestion_info = {
            "id": f"suggestion_{int(time.time())}_{category}",
            "text": suggestion_text,
            "category": category,
            "priority": "high" if rating == 1 else "medium",
            "source": "automatic",
            "feedback_id": feedback_info["id"],
            "created_at": datetime.now().isoformat(),
            "status": "new"
        }
        
        # Adicionar sugestão
        self.suggestions["suggestions"].append(suggestion_info)
        self._save_suggestions()
        
        # Notificar sobre nova sugestão
        notification_system.create_notification(
            f"Nova sugestão: {category}",
            suggestion_text,
            "warning" if rating == 1 else "info",
            "feedback",
            {
                "category": category,
                "priority": suggestion_info["priority"],
                "suggestion_id": suggestion_info["id"]
            }
        )
    
    def submit_suggestion(self, text: str, category: str, priority: str = "medium",
                         source: str = "manual", metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Submete sugestão
        
        Args:
            text: Texto da sugestão
            category: Categoria da sugestão
            priority: Prioridade da sugestão ("low", "medium", "high")
            source: Fonte da sugestão
            metadata: Metadados adicionais
            
        Returns:
            Dict: Informações da sugestão
        """
        # Validar categoria
        valid_categories = ["usability", "performance", "feature", "bug", "documentation", "other"]
        if category not in valid_categories:
            return {
                "success": False,
                "error": f"Categoria inválida. Categorias válidas: {', '.join(valid_categories)}"
            }
        
        # Validar prioridade
        valid_priorities = ["low", "medium", "high"]
        if priority not in valid_priorities:
            return {
                "success": False,
                "error": f"Prioridade inválida. Prioridades válidas: {', '.join(valid_priorities)}"
            }
        
        # Criar sugestão
        suggestion_info = {
            "id": f"suggestion_{int(time.time())}_{category}",
            "text": text,
            "category": category,
            "priority": priority,
            "source": source,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "status": "new"
        }
        
        # Adicionar sugestão
        self.suggestions["suggestions"].append(suggestion_info)
        self._save_suggestions()
        
        # Notificar sobre nova sugestão
        notification_system.create_notification(
            f"Nova sugestão: {category}",
            text,
            "warning" if priority == "high" else "info",
            "feedback",
            {
                "category": category,
                "priority": priority,
                "suggestion_id": suggestion_info["id"]
            }
        )
        
        return {
            "success": True,
            "suggestion": suggestion_info
        }
    
    def update_feedback_status(self, feedback_id: str, status: str) -> Dict[str, Any]:
        """
        Atualiza status de feedback
        
        Args:
            feedback_id: ID do feedback
            status: Novo status
            
        Returns:
            Dict: Resultado da atualização
        """
        # Validar status
        valid_statuses = ["new", "in_progress", "resolved", "closed"]
        if status not in valid_statuses:
            return {
                "success": False,
                "error": f"Status inválido. Status válidos: {', '.join(valid_statuses)}"
            }
        
        # Procurar feedback
        for feedback in self.feedback["feedback"]:
            if feedback["id"] == feedback_id:
                # Atualizar status
                old_status = feedback["status"]
                feedback["status"] = status
                feedback["updated_at"] = datetime.now().isoformat()
                
                # Salvar feedback
                self._save_feedback()
                
                # Notificar sobre atualização de status
                notification_system.create_notification(
                    f"Status de feedback atualizado: {feedback_id}",
                    f"Status de feedback atualizado de {old_status} para {status}",
                    "info",
                    "feedback",
                    {
                        "feedback_id": feedback_id,
                        "old_status": old_status,
                        "new_status": status
                    }
                )
                
                return {
                    "success": True,
                    "feedback": feedback
                }
        
        return {
            "success": False,
            "error": f"Feedback {feedback_id} não encontrado"
        }
    
    def update_suggestion_status(self, suggestion_id: str, status: str) -> Dict[str, Any]:
        """
        Atualiza status de sugestão
        
        Args:
            suggestion_id: ID da sugestão
            status: Novo status
            
        Returns:
            Dict: Resultado da atualização
        """
        # Validar status
        valid_statuses = ["new", "in_progress", "implemented", "rejected"]
        if status not in valid_statuses:
            return {
                "success": False,
                "error": f"Status inválido. Status válidos: {', '.join(valid_statuses)}"
            }
        
        # Procurar sugestão
        for suggestion in self.suggestions["suggestions"]:
            if suggestion["id"] == suggestion_id:
                # Atualizar status
                old_status = suggestion["status"]
                suggestion["status"] = status
                suggestion["updated_at"] = datetime.now().isoformat()
                
                # Salvar sugestões
                self._save_suggestions()
                
                # Notificar sobre atualização de status
                notification_system.create_notification(
                    f"Status de sugestão atualizado: {suggestion_id}",
                    f"Status de sugestão atualizado de {old_status} para {status}",
                    "info",
                    "feedback",
                    {
                        "suggestion_id": suggestion_id,
                        "old_status": old_status,
                        "new_status": status
                    }
                )
                
                return {
                    "success": True,
                    "suggestion": suggestion
                }
        
        return {
            "success": False,
            "error": f"Sugestão {suggestion_id} não encontrada"
        }
    
    def get_feedback(self, feedback_id: str = None, category: str = None, status: str = None) -> Dict[str, Any]:
        """
        Obtém feedback
        
        Args:
            feedback_id: ID do feedback
            category: Categoria do feedback
            status: Status do feedback
            
        Returns:
            Dict: Feedback
        """
        # Se ID for fornecido, retornar feedback específico
        if feedback_id:
            for feedback in self.feedback["feedback"]:
                if feedback["id"] == feedback_id:
                    return {
                        "success": True,
                        "feedback": feedback
                    }
            
            return {
                "success": False,
                "error": f"Feedback {feedback_id} não encontrado"
            }
        
        # Filtrar feedback
        filtered_feedback = self.feedback["feedback"]
        
        if category:
            filtered_feedback = [f for f in filtered_feedback if f["category"] == category]
        
        if status:
            filtered_feedback = [f for f in filtered_feedback if f["status"] == status]
        
        # Ordenar por data de criação (mais recentes primeiro)
        filtered_feedback = sorted(filtered_feedback, key=lambda f: f["created_at"], reverse=True)
        
        return {
            "success": True,
            "feedback": filtered_feedback,
            "count": len(filtered_feedback)
        }
    
    def get_suggestions(self, suggestion_id: str = None, category: str = None,
                       priority: str = None, status: str = None) -> Dict[str, Any]:
        """
        Obtém sugestões
        
        Args:
            suggestion_id: ID da sugestão
            category: Categoria da sugestão
            priority: Prioridade da sugestão
            status: Status da sugestão
            
        Returns:
            Dict: Sugestões
        """
        # Se ID for fornecido, retornar sugestão específica
        if suggestion_id:
            for suggestion in self.suggestions["suggestions"]:
                if suggestion["id"] == suggestion_id:
                    return {
                        "success": True,
                        "suggestion": suggestion
                    }
            
            return {
                "success": False,
                "error": f"Sugestão {suggestion_id} não encontrada"
            }
        
        # Filtrar sugestões
        filtered_suggestions = self.suggestions["suggestions"]
        
        if category:
            filtered_suggestions = [s for s in filtered_suggestions if s["category"] == category]
        
        if priority:
            filtered_suggestions = [s for s in filtered_suggestions if s["priority"] == priority]
        
        if status:
            filtered_suggestions = [s for s in filtered_suggestions if s["status"] == status]
        
        # Ordenar por prioridade e data de criação
        priority_order = {"high": 0, "medium": 1, "low": 2}
        filtered_suggestions = sorted(filtered_suggestions, key=lambda s: (priority_order.get(s["priority"], 3), s["created_at"]), reverse=True)
        
        return {
            "success": True,
            "suggestions": filtered_suggestions,
            "count": len(filtered_suggestions)
        }
    
    def get_feedback_summary(self) -> Dict[str, Any]:
        """
        Obtém resumo de feedback
        
        Returns:
            Dict: Resumo de feedback
        """
        # Contar feedback por categoria
        categories = {}
        for feedback in self.feedback["feedback"]:
            category = feedback["category"]
            if category not in categories:
                categories[category] = 0
            categories[category] += 1
        
        # Contar feedback por status
        statuses = {}
        for feedback in self.feedback["feedback"]:
            status = feedback["status"]
            if status not in statuses:
                statuses[status] = 0
            statuses[status] += 1
        
        # Calcular média de avaliações
        ratings = [f["rating"] for f in self.feedback["feedback"] if "rating" in f]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        return {
            "success": True,
            "total_feedback": len(self.feedback["feedback"]),
            "categories": categories,
            "statuses": statuses,
            "average_rating": avg_rating,
            "updated_at": self.feedback["updated_at"]
        }
    
    def get_suggestions_summary(self) -> Dict[str, Any]:
        """
        Obtém resumo de sugestões
        
        Returns:
            Dict: Resumo de sugestões
        """
        # Contar sugestões por categoria
        categories = {}
        for suggestion in self.suggestions["suggestions"]:
            category = suggestion["category"]
            if category not in categories:
                categories[category] = 0
            categories[category] += 1
        
        # Contar sugestões por prioridade
        priorities = {}
        for suggestion in self.suggestions["suggestions"]:
            priority = suggestion["priority"]
            if priority not in priorities:
                priorities[priority] = 0
            priorities[priority] += 1
        
        # Contar sugestões por status
        statuses = {}
        for suggestion in self.suggestions["suggestions"]:
            status = suggestion["status"]
            if status not in statuses:
                statuses[status] = 0
            statuses[status] += 1
        
        return {
            "success": True,
            "total_suggestions": len(self.suggestions["suggestions"]),
            "categories": categories,
            "priorities": priorities,
            "statuses": statuses,
            "updated_at": self.suggestions["updated_at"]
        }
    
    def register_feedback_callback(self, category: str, callback: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Registra callback para feedback
        
        Args:
            category: Categoria do feedback
            callback: Função a ser chamada quando um feedback for submetido
            
        Returns:
            bool: True se callback foi registrado, False caso contrário
        """
        # Inicializar lista de callbacks se não existir
        if category not in self.feedback_callbacks:
            self.feedback_callbacks[category] = []
        
        # Adicionar callback
        self.feedback_callbacks[category].append(callback)
        
        return True
    
    def _execute_feedback_callbacks(self, feedback_info: Dict[str, Any]) -> None:
        """
        Executa callbacks para feedback
        
        Args:
            feedback_info: Informações do feedback
        """
        category = feedback_info["category"]
        
        # Executar callbacks específicos para a categoria
        if category in self.feedback_callbacks:
            for callback in self.feedback_callbacks[category]:
                try:
                    callback(feedback_info)
                except Exception as e:
                    print(f"Erro ao executar callback para feedback {category}: {str(e)}")
        
        # Executar callbacks para todas as categorias
        if "all" in self.feedback_callbacks:
            for callback in self.feedback_callbacks["all"]:
                try:
                    callback(feedback_info)
                except Exception as e:
                    print(f"Erro ao executar callback para feedback {category}: {str(e)}")

# Instância global para uso em todo o sistema
feedback_system = FeedbackSystem()
