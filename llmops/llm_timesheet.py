#!/usr/bin/env python3
"""
LLM Timesheet - Sistema de "Bater o Ponto" para LLMs

Um sistema que registra e organiza automaticamente as contribuições de diferentes
LLMs em um projeto, permitindo rastrear quem fez o quê, quando e por quê.
"""

import os
import sys
import json
import uuid
import time
import logging
import argparse
import hashlib
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import subprocess

# Configurações
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TIMESHEET_DIR = os.path.join(BASE_DIR, "llmops", "timesheets")
SPRINTS_DIR = os.path.join(BASE_DIR, "llmops", "sprints")
REPORTS_DIR = os.path.join(BASE_DIR, "llmops", "reports")
CONFIG_FILE = os.path.join(BASE_DIR, "llmops", "config.json")
LOG_FILE = os.path.join(BASE_DIR, "llmops", "llm-timesheet.log")

# Criar diretórios necessários
os.makedirs(TIMESHEET_DIR, exist_ok=True)
os.makedirs(SPRINTS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=LOG_FILE,
    filemode="a"
)
logger = logging.getLogger("llm-timesheet")

# Carregar ou criar configuração
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
else:
    config = {
        "project_name": os.path.basename(os.path.dirname(BASE_DIR)),
        "current_sprint": "sprint-1",
        "sprint_duration_days": 7,
        "known_llms": ["claude", "gpt-4", "gemini", "llama"],
        "timesheet_format": "json",
        "auto_organize": True,
        "organization_rules": {
            "code": ["*.py", "*.js", "*.html", "*.css", "*.sh"],
            "documentation": ["*.md", "README*", "*.txt"],
            "configuration": ["*.json", "*.yml", "*.yaml", "*.toml"],
            "data": ["*.csv", "*.json", "*.xml"]
        }
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

class LLMTimesheet:
    """Sistema de registro de tempo para LLMs"""
    
    def __init__(self):
        """Inicializa o sistema de timesheet"""
        self.config = config
        self.current_sprint = self.config["current_sprint"]
        
        # Carregar sprint atual
        self.sprint_path = os.path.join(SPRINTS_DIR, f"{self.current_sprint}.json")
        if os.path.exists(self.sprint_path):
            with open(self.sprint_path, 'r') as f:
                self.sprint = json.load(f)
        else:
            # Criar novo sprint
            start_date = datetime.now().isoformat()
            duration_days = self.config["sprint_duration_days"]
            self.sprint = {
                "sprint_id": self.current_sprint,
                "project_name": self.config["project_name"],
                "start_date": start_date,
                "end_date": None,
                "status": "active",
                "tasks": [],
                "contributors": {},
                "summary": None
            }
            self._save_sprint()
    
    def _save_sprint(self):
        """Salva o sprint atual"""
        with open(self.sprint_path, 'w') as f:
            json.dump(self.sprint, f, indent=2)
    
    def punch_in(self, llm_name: str, task_description: str, context: Optional[str] = None) -> str:
        """
        Registra o início de uma tarefa por um LLM
        
        Args:
            llm_name: Nome do LLM
            task_description: Descrição da tarefa
            context: Contexto adicional (opcional)
            
        Returns:
            ID da tarefa criada
        """
        logger.info(f"Punch in: {llm_name} - {task_description}")
        
        # Gerar ID único para a tarefa
        task_id = str(uuid.uuid4())
        
        # Criar registro de tarefa
        task = {
            "task_id": task_id,
            "llm_name": llm_name,
            "description": task_description,
            "context": context,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "status": "in_progress",
            "files_modified": [],
            "summary": None
        }
        
        # Adicionar tarefa ao sprint
        self.sprint["tasks"].append(task)
        
        # Atualizar contribuidores
        if llm_name not in self.sprint["contributors"]:
            self.sprint["contributors"][llm_name] = {
                "tasks_completed": 0,
                "tasks_in_progress": 1,
                "total_time": 0
            }
        else:
            self.sprint["contributors"][llm_name]["tasks_in_progress"] += 1
        
        # Salvar sprint
        self._save_sprint()
        
        # Criar timesheet
        timesheet = {
            "task_id": task_id,
            "llm_name": llm_name,
            "sprint_id": self.current_sprint,
            "description": task_description,
            "context": context,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "duration_seconds": 0,
            "files_modified": [],
            "summary": None
        }
        
        # Salvar timesheet
        timesheet_path = os.path.join(TIMESHEET_DIR, f"{task_id}.json")
        with open(timesheet_path, 'w') as f:
            json.dump(timesheet, f, indent=2)
        
        return task_id
    
    def punch_out(self, task_id: str, summary: str, files_modified: List[str] = None) -> Dict[str, Any]:
        """
        Registra o fim de uma tarefa
        
        Args:
            task_id: ID da tarefa
            summary: Resumo do que foi feito
            files_modified: Lista de arquivos modificados (opcional)
            
        Returns:
            Dados da tarefa atualizada
        """
        logger.info(f"Punch out: {task_id}")
        
        # Carregar timesheet
        timesheet_path = os.path.join(TIMESHEET_DIR, f"{task_id}.json")
        if not os.path.exists(timesheet_path):
            logger.error(f"Timesheet não encontrada: {task_id}")
            return {"error": "Timesheet não encontrada"}
        
        with open(timesheet_path, 'r') as f:
            timesheet = json.load(f)
        
        # Atualizar timesheet
        timesheet["end_time"] = datetime.now().isoformat()
        timesheet["summary"] = summary
        
        # Calcular duração
        start_time = datetime.fromisoformat(timesheet["start_time"])
        end_time = datetime.fromisoformat(timesheet["end_time"])
        duration_seconds = (end_time - start_time).total_seconds()
        timesheet["duration_seconds"] = duration_seconds
        
        # Adicionar arquivos modificados
        if files_modified:
            timesheet["files_modified"] = files_modified
        
        # Atualizar tarefa no sprint
        for task in self.sprint["tasks"]:
            if task["task_id"] == task_id:
                task["end_time"] = timesheet["end_time"]
                task["status"] = "completed"
                task["summary"] = summary
                if files_modified:
                    task["files_modified"] = files_modified
                
                # Atualizar contribuidor
                llm_name = task["llm_name"]
                self.sprint["contributors"][llm_name]["tasks_completed"] += 1
                self.sprint["contributors"][llm_name]["tasks_in_progress"] -= 1
                self.sprint["contributors"][llm_name]["total_time"] += duration_seconds
                break
        
        # Salvar timesheet e sprint
        with open(timesheet_path, 'w') as f:
            json.dump(timesheet, f, indent=2)
        self._save_sprint()
        
        # Organizar arquivos modificados se configurado
        if self.config["auto_organize"] and files_modified:
            self._organize_files(files_modified)
        
        return timesheet
    
    def _organize_files(self, files: List[str]):
        """
        Organiza os arquivos modificados
        
        Args:
            files: Lista de caminhos de arquivos
        """
        logger.info(f"Organizando {len(files)} arquivos")
        
        # Mapear arquivos para categorias
        categorized_files = {}
        for file_path in files:
            if not os.path.exists(file_path):
                continue
            
            # Determinar categoria
            category = self._categorize_file(file_path)
            if category not in categorized_files:
                categorized_files[category] = []
            
            categorized_files[category].append(file_path)
        
        # Gerar relatório de organização
        report = {
            "timestamp": datetime.now().isoformat(),
            "sprint_id": self.current_sprint,
            "categories": {}
        }
        
        for category, files in categorized_files.items():
            report["categories"][category] = {
                "count": len(files),
                "files": [os.path.basename(f) for f in files]
            }
        
        # Salvar relatório
        report_path = os.path.join(REPORTS_DIR, f"organization_{int(time.time())}.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
    
    def _categorize_file(self, file_path: str) -> str:
        """
        Categoriza um arquivo com base em seu nome e extensão
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Categoria do arquivo
        """
        basename = os.path.basename(file_path)
        
        # Verificar cada categoria nas regras
        for category, patterns in self.config["organization_rules"].items():
            for pattern in patterns:
                if self._match_pattern(basename, pattern):
                    return category
        
        # Categoria padrão
        return "other"
    
    def _match_pattern(self, filename: str, pattern: str) -> bool:
        """
        Verifica se um nome de arquivo corresponde a um padrão
        
        Args:
            filename: Nome do arquivo
            pattern: Padrão (com glob)
            
        Returns:
            True se corresponder, False caso contrário
        """
        # Converter padrão glob para regex
        regex_pattern = pattern.replace(".", "\\.").replace("*", ".*")
        return bool(re.match(f"^{regex_pattern}$", filename))
    
    def create_sprint_report(self) -> Dict[str, Any]:
        """
        Cria um relatório do sprint atual
        
        Returns:
            Dados do relatório
        """
        logger.info(f"Criando relatório do sprint: {self.current_sprint}")
        
        # Calcular estatísticas
        total_tasks = len(self.sprint["tasks"])
        completed_tasks = sum(1 for task in self.sprint["tasks"] if task["status"] == "completed")
        in_progress_tasks = sum(1 for task in self.sprint["tasks"] if task["status"] == "in_progress")
        
        # Arquivos modificados
        files_modified = set()
        for task in self.sprint["tasks"]:
            if "files_modified" in task and task["files_modified"]:
                files_modified.update(task["files_modified"])
        
        # Organizar arquivos por categoria
        files_by_category = {}
        for file_path in files_modified:
            category = self._categorize_file(file_path)
            if category not in files_by_category:
                files_by_category[category] = []
            files_by_category[category].append(os.path.basename(file_path))
        
        # Criar relatório
        report = {
            "sprint_id": self.current_sprint,
            "project_name": self.config["project_name"],
            "start_date": self.sprint["start_date"],
            "end_date": datetime.now().isoformat() if not self.sprint["end_date"] else self.sprint["end_date"],
            "status": self.sprint["status"],
            "statistics": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "in_progress_tasks": in_progress_tasks,
                "completion_rate": completed_tasks / total_tasks if total_tasks > 0 else 0,
                "total_files_modified": len(files_modified)
            },
            "contributors": self.sprint["contributors"],
            "files_by_category": files_by_category,
            "tasks": [
                {
                    "task_id": task["task_id"],
                    "llm_name": task["llm_name"],
                    "description": task["description"],
                    "status": task["status"],
                    "summary": task["summary"]
                }
                for task in self.sprint["tasks"]
            ]
        }
        
        # Salvar relatório
        report_path = os.path.join(REPORTS_DIR, f"{self.current_sprint}_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def finish_sprint(self, summary: str) -> Dict[str, Any]:
        """
        Finaliza o sprint atual
        
        Args:
            summary: Resumo do sprint
            
        Returns:
            Dados do relatório final
        """
        logger.info(f"Finalizando sprint: {self.current_sprint}")
        
        # Finalizar tarefas em andamento
        for task in self.sprint["tasks"]:
            if task["status"] == "in_progress":
                task["status"] = "incomplete"
        
        # Atualizar sprint
        self.sprint["status"] = "completed"
        self.sprint["end_date"] = datetime.now().isoformat()
        self.sprint["summary"] = summary
        self._save_sprint()
        
        # Criar relatório final
        report = self.create_sprint_report()
        
        # Incrementar número do sprint
        sprint_num = int(self.current_sprint.split("-")[1])
        next_sprint = f"sprint-{sprint_num + 1}"
        
        # Atualizar configuração
        self.config["current_sprint"] = next_sprint
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        # Inicializar próximo sprint
        self.current_sprint = next_sprint
        self.sprint = {
            "sprint_id": self.current_sprint,
            "project_name": self.config["project_name"],
            "start_date": datetime.now().isoformat(),
            "end_date": None,
            "status": "active",
            "tasks": [],
            "contributors": {},
            "summary": None
        }
        self._save_sprint()
        
        return report
    
    def detect_modified_files(self, since: Optional[str] = None) -> List[str]:
        """
        Detecta arquivos modificados no diretório do projeto
        
        Args:
            since: Timestamp de início (opcional)
            
        Returns:
            Lista de arquivos modificados
        """
        logger.info("Detectando arquivos modificados")
        
        # Determinar diretório base
        base_dir = BASE_DIR
        
        # Usar git se disponível
        try:
            if os.path.exists(os.path.join(base_dir, ".git")):
                if since:
                    # Converter timestamp ISO para formato git
                    dt = datetime.fromisoformat(since)
                    git_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                    cmd = ["git", "-C", base_dir, "diff", "--name-only", f"--since=\"{git_time}\""]
                else:
                    cmd = ["git", "-C", base_dir, "diff", "--name-only"]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    files = [os.path.join(base_dir, f) for f in result.stdout.strip().split("\n") if f]
                    return files
        except Exception as e:
            logger.warning(f"Erro ao usar git: {e}")
        
        # Alternativa: usar modificação de arquivos
        files = []
        if since:
            since_dt = datetime.fromisoformat(since)
            since_timestamp = since_dt.timestamp()
            
            for root, _, filenames in os.walk(base_dir):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    try:
                        mtime = os.path.getmtime(file_path)
                        if mtime >= since_timestamp:
                            files.append(file_path)
                    except Exception:
                        pass
        
        return files

# Função principal para CLI
def main():
    parser = argparse.ArgumentParser(description="LLM Timesheet - Sistema de Bater o Ponto para LLMs")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")
    
    # Comando punch-in
    punch_in_parser = subparsers.add_parser("punch-in", help="Registrar início de tarefa")
    punch_in_parser.add_argument("--llm", required=True, help="Nome do LLM")
    punch_in_parser.add_argument("--task", required=True, help="Descrição da tarefa")
    punch_in_parser.add_argument("--context", help="Contexto adicional")
    
    # Comando punch-out
    punch_out_parser = subparsers.add_parser("punch-out", help="Registrar fim de tarefa")
    punch_out_parser.add_argument("--task-id", required=True, help="ID da tarefa")
    punch_out_parser.add_argument("--summary", required=True, help="Resumo do trabalho realizado")
    punch_out_parser.add_argument("--files", nargs="+", help="Arquivos modificados")
    punch_out_parser.add_argument("--detect-files", action="store_true", help="Detectar arquivos modificados automaticamente")
    
    # Comando report
    report_parser = subparsers.add_parser("report", help="Gerar relatório de sprint")
    
    # Comando finish-sprint
    finish_parser = subparsers.add_parser("finish-sprint", help="Finalizar sprint atual")
    finish_parser.add_argument("--summary", required=True, help="Resumo do sprint")
    
    # Parsear argumentos
    args = parser.parse_args()
    
    # Inicializar timesheet
    timesheet = LLMTimesheet()
    
    # Executar comando
    if args.command == "punch-in":
        task_id = timesheet.punch_in(args.llm, args.task, args.context)
        print(f"✅ Tarefa registrada com ID: {task_id}")
        
    elif args.command == "punch-out":
        files_modified = None
        
        if args.detect_files:
            # Carregar timesheet para obter tempo de início
            timesheet_path = os.path.join(TIMESHEET_DIR, f"{args.task_id}.json")
            if os.path.exists(timesheet_path):
                with open(timesheet_path, 'r') as f:
                    task_data = json.load(f)
                    start_time = task_data.get("start_time")
                    if start_time:
                        files_modified = timesheet.detect_modified_files(start_time)
        elif args.files:
            files_modified = args.files
        
        result = timesheet.punch_out(args.task_id, args.summary, files_modified)
        
        if "error" in result:
            print(f"❌ Erro: {result['error']}")
        else:
            duration_seconds = result.get("duration_seconds", 0)
            duration_minutes = duration_seconds / 60
            print(f"✅ Tarefa finalizada. Duração: {duration_minutes:.2f} minutos.")
            if files_modified:
                print(f"📝 {len(files_modified)} arquivos modificados.")
        
    elif args.command == "report":
        report = timesheet.create_sprint_report()
        print(f"✅ Relatório gerado para o sprint {report['sprint_id']}")
        print(f"📊 Tarefas: {report['statistics']['completed_tasks']}/{report['statistics']['total_tasks']} concluídas")
        print(f"📁 Arquivos modificados: {report['statistics']['total_files_modified']}")
        
        # Exibir contribuidores
        print("\n👥 Contribuidores:")
        for llm, stats in report["contributors"].items():
            print(f"  - {llm}: {stats['tasks_completed']} tarefas concluídas, {stats['total_time'] / 60:.2f} minutos")
        
        print(f"\n📄 Relatório completo: {os.path.join(REPORTS_DIR, f'{report['sprint_id']}_report.json')}")
        
    elif args.command == "finish-sprint":
        report = timesheet.finish_sprint(args.summary)
        print(f"✅ Sprint {report['sprint_id']} finalizado!")
        print(f"📊 Conclusão: {report['statistics']['completion_rate'] * 100:.2f}%")
        print(f"⏭️ Próximo sprint: {timesheet.current_sprint}")
        
        print(f"\n📄 Relatório final: {os.path.join(REPORTS_DIR, f'{report['sprint_id']}_report.json')}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()