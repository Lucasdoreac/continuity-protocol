#!/usr/bin/env python3
"""
LLM Timesheet MCP Integration

Este módulo integra o sistema de timesheet de LLMs com o servidor MCP Continuity,
permitindo que o timesheet seja acessado via protocolo MCP.
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# Ajustar path para importar o módulo de timesheet
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llmops.llm_timesheet import LLMTimesheet

class LLMTimesheetMCP:
    """Adaptador MCP para o sistema de timesheet de LLMs"""
    
    def __init__(self):
        """Inicializa o adaptador MCP"""
        self.timesheet = LLMTimesheet()
    
    def punch_in(self, llm_name: str, task_description: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Registra o início de uma tarefa por um LLM via MCP
        
        Args:
            llm_name: Nome do LLM
            task_description: Descrição da tarefa
            context: Contexto adicional (opcional)
            
        Returns:
            Informações sobre a tarefa criada
        """
        task_id = self.timesheet.punch_in(llm_name, task_description, context)
        
        return {
            "success": True,
            "task_id": task_id,
            "llm_name": llm_name,
            "task_description": task_description,
            "start_time": datetime.now().isoformat()
        }
    
    def punch_out(self, task_id: str, summary: str, detect_files: bool = False) -> Dict[str, Any]:
        """
        Registra o fim de uma tarefa via MCP
        
        Args:
            task_id: ID da tarefa
            summary: Resumo do que foi feito
            detect_files: Se deve detectar arquivos modificados automaticamente
            
        Returns:
            Informações sobre a tarefa finalizada
        """
        files_modified = None
        
        if detect_files:
            # Carregar timesheet para obter tempo de início
            timesheet_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "llmops", "timesheets"
            )
            timesheet_path = os.path.join(timesheet_dir, f"{task_id}.json")
            
            if os.path.exists(timesheet_path):
                with open(timesheet_path, 'r') as f:
                    task_data = json.load(f)
                    start_time = task_data.get("start_time")
                    if start_time:
                        files_modified = self.timesheet.detect_modified_files(start_time)
        
        result = self.timesheet.punch_out(task_id, summary, files_modified)
        
        if "error" in result:
            return {
                "success": False,
                "error": result["error"]
            }
        else:
            return {
                "success": True,
                "task_id": task_id,
                "duration_seconds": result.get("duration_seconds", 0),
                "end_time": result.get("end_time"),
                "files_modified": len(result.get("files_modified", [])),
                "summary": summary
            }
    
    def get_sprint_report(self) -> Dict[str, Any]:
        """
        Obtém relatório do sprint atual via MCP
        
        Returns:
            Relatório resumido do sprint
        """
        report = self.timesheet.create_sprint_report()
        
        # Versão simplificada para MCP
        return {
            "success": True,
            "sprint_id": report["sprint_id"],
            "project_name": report["project_name"],
            "status": report["status"],
            "statistics": report["statistics"],
            "contributors": report["contributors"]
        }
    
    def finish_sprint(self, summary: str) -> Dict[str, Any]:
        """
        Finaliza o sprint atual via MCP
        
        Args:
            summary: Resumo do sprint
            
        Returns:
            Informações sobre o sprint finalizado
        """
        report = self.timesheet.finish_sprint(summary)
        
        return {
            "success": True,
            "sprint_id": report["sprint_id"],
            "completion_rate": report["statistics"]["completion_rate"],
            "next_sprint": self.timesheet.current_sprint
        }
    
    def list_active_tasks(self) -> Dict[str, Any]:
        """
        Lista tarefas ativas no sprint atual
        
        Returns:
            Lista de tarefas ativas
        """
        active_tasks = []
        
        for task in self.timesheet.sprint["tasks"]:
            if task["status"] == "in_progress":
                active_tasks.append({
                    "task_id": task["task_id"],
                    "llm_name": task["llm_name"],
                    "description": task["description"],
                    "start_time": task["start_time"]
                })
        
        return {
            "success": True,
            "sprint_id": self.timesheet.current_sprint,
            "active_tasks": active_tasks,
            "count": len(active_tasks)
        }
    
    def get_task_details(self, task_id: str) -> Dict[str, Any]:
        """
        Obtém detalhes de uma tarefa específica
        
        Args:
            task_id: ID da tarefa
            
        Returns:
            Detalhes da tarefa
        """
        # Tentar carregar do sprint atual
        for task in self.timesheet.sprint["tasks"]:
            if task["task_id"] == task_id:
                return {
                    "success": True,
                    "task_id": task["task_id"],
                    "llm_name": task["llm_name"],
                    "description": task["description"],
                    "status": task["status"],
                    "start_time": task["start_time"],
                    "end_time": task.get("end_time"),
                    "summary": task.get("summary"),
                    "files_modified": len(task.get("files_modified", []))
                }
        
        # Se não encontrar, tentar carregar da timesheet
        timesheet_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "llmops", "timesheets"
        )
        timesheet_path = os.path.join(timesheet_dir, f"{task_id}.json")
        
        if os.path.exists(timesheet_path):
            with open(timesheet_path, 'r') as f:
                task_data = json.load(f)
                return {
                    "success": True,
                    "task_id": task_data["task_id"],
                    "llm_name": task_data["llm_name"],
                    "description": task_data["description"],
                    "status": "completed" if task_data.get("end_time") else "in_progress",
                    "start_time": task_data["start_time"],
                    "end_time": task_data.get("end_time"),
                    "summary": task_data.get("summary"),
                    "files_modified": len(task_data.get("files_modified", []))
                }
        
        return {
            "success": False,
            "error": f"Task not found: {task_id}"
        }