#!/usr/bin/env python3
"""
Continuity Protocol Server - Implementação do Protocolo de Continuidade de Projetos (PCP)

Este servidor implementa o Protocolo de Continuidade de Projetos, permitindo:
- Registro e descoberta de projetos
- Armazenamento e recuperação de contexto
- Gerenciamento de sessões de trabalho
- Comunicação entre diferentes agentes de IA
"""

import os
import sys
import json
import uuid
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

# Configurações globais
BASE_DIR = "/Users/lucascardoso/apps/MCP/CONTINUITY"
DATA_DIR = os.path.join(BASE_DIR, "data")
PROJECTS_DIR = os.path.join(DATA_DIR, "projects")
SESSIONS_DIR = os.path.join(DATA_DIR, "sessions")
ARTIFACTS_DIR = os.path.join(DATA_DIR, "artifacts")
LOG_DIR = os.path.join(BASE_DIR, "logs")
VERSION = "1.0.0"

# Configurar logging
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.path.join(LOG_DIR, "continuity-protocol.log"),
    filemode="a"
)
logger = logging.getLogger("continuity-protocol")

# Criar diretórios necessários
os.makedirs(PROJECTS_DIR, exist_ok=True)
os.makedirs(SESSIONS_DIR, exist_ok=True)
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

# Importar FastMCP
try:
    from mcp.server.fastmcp import FastMCP
    logger.info("FastMCP importado com sucesso")
except ImportError:
    logger.warning("Instalando pacote MCP...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "mcp"])
    from mcp.server.fastmcp import FastMCP

class ContinuityProtocolServer:
    """
    Servidor do Protocolo de Continuidade de Projetos
    
    Implementa as operações básicas do protocolo:
    - Gerenciamento de projetos
    - Armazenamento de contexto
    - Gerenciamento de sessões
    - Armazenamento de artefatos
    """
    
    def __init__(self, server_name="continuity-protocol"):
        """
        Inicializa o servidor do Protocolo de Continuidade
        
        Args:
            server_name (str): Nome do servidor MCP
        """
        self.server_name = server_name
        logger.info(f"Inicializando servidor: {server_name}")
        
        # Inicializar FastMCP
        self.mcp = FastMCP(server_name)
        
        # Salvar PID para gerenciamento
        self._save_pid()
        
        # Registrar ferramentas MCP
        self._register_tools()
        
        logger.info("Servidor inicializado com sucesso")
        print(f"Continuity Protocol Server v{VERSION}")
        print(f"- Projetos: {PROJECTS_DIR}")
        print(f"- Sessões: {SESSIONS_DIR}")
        print(f"- Artefatos: {ARTIFACTS_DIR}")
    
    def _save_pid(self):
        """Salva o PID do processo para gerenciamento"""
        pid_file = os.path.join(BASE_DIR, "continuity-protocol.pid")
        with open(pid_file, "w") as f:
            f.write(str(os.getpid()))
        logger.info(f"PID salvo: {os.getpid()}")
    
    def _register_tools(self):
        """Registra todas as ferramentas do protocolo"""
        # Ferramentas de projeto
        self._register_project_tools()
        
        # Ferramentas de contexto
        self._register_context_tools()
        
        # Ferramentas de sessão
        self._register_session_tools()
        
        # Ferramentas de artefato
        self._register_artifact_tools()
    
    def _register_project_tools(self):
        """Registra ferramentas relacionadas a projetos"""
        
        @self.mcp.tool()
        def project_list() -> str:
            """Lista todos os projetos disponíveis"""
            logger.info("Listando projetos")
            
            projects = []
            for project_file in os.listdir(PROJECTS_DIR):
                if project_file.endswith(".json"):
                    with open(os.path.join(PROJECTS_DIR, project_file), "r") as f:
                        project = json.load(f)
                        projects.append({
                            "project_id": project["project_id"],
                            "name": project["name"],
                            "description": project["description"],
                            "status": project["status"],
                            "updated_at": project["updated_at"]
                        })
            
            return json.dumps({"projects": projects}, indent=2)
        
        @self.mcp.tool()
        def project_get(project_id: str) -> str:
            """
            Recupera detalhes de um projeto específico
            
            Args:
                project_id: ID único do projeto
            """
            logger.info(f"Recuperando projeto: {project_id}")
            
            project_file = os.path.join(PROJECTS_DIR, f"{project_id}.json")
            if not os.path.exists(project_file):
                logger.error(f"Projeto não encontrado: {project_id}")
                return json.dumps({"error": "Projeto não encontrado"}, indent=2)
            
            with open(project_file, "r") as f:
                project = json.load(f)
            
            return json.dumps(project, indent=2)
        
        @self.mcp.tool()
        def project_create(name: str, description: str, domain: str = "", metadata_json: str = "{}") -> str:
            """
            Cria um novo projeto
            
            Args:
                name: Nome do projeto
                description: Descrição do projeto
                domain: Domínio do projeto (opcional)
                metadata_json: Metadados adicionais em formato JSON (opcional)
            """
            logger.info(f"Criando projeto: {name}")
            
            # Gerar ID único para o projeto
            project_id = str(uuid.uuid4())
            
            # Parsear metadados
            try:
                metadata = json.loads(metadata_json)
            except:
                metadata = {}
            
            # Criar projeto
            project = {
                "project_id": project_id,
                "name": name,
                "description": description,
                "domain": domain,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "status": "active",
                "endpoints": {
                    "context": f"/api/projects/{project_id}/context",
                    "artifacts": f"/api/projects/{project_id}/artifacts",
                    "sessions": f"/api/projects/{project_id}/sessions"
                },
                "metadata": metadata
            }
            
            # Salvar projeto
            project_file = os.path.join(PROJECTS_DIR, f"{project_id}.json")
            with open(project_file, "w") as f:
                json.dump(project, f, indent=2)
            
            # Criar diretórios para o projeto
            os.makedirs(os.path.join(SESSIONS_DIR, project_id), exist_ok=True)
            os.makedirs(os.path.join(ARTIFACTS_DIR, project_id), exist_ok=True)
            
            return json.dumps(project, indent=2)
        
        @self.mcp.tool()
        def project_update(project_id: str, name: str = None, description: str = None, 
                           status: str = None, metadata_json: str = None) -> str:
            """
            Atualiza um projeto existente
            
            Args:
                project_id: ID único do projeto
                name: Novo nome do projeto (opcional)
                description: Nova descrição do projeto (opcional)
                status: Novo status do projeto (opcional)
                metadata_json: Novos metadados em formato JSON (opcional)
            """
            logger.info(f"Atualizando projeto: {project_id}")
            
            project_file = os.path.join(PROJECTS_DIR, f"{project_id}.json")
            if not os.path.exists(project_file):
                logger.error(f"Projeto não encontrado: {project_id}")
                return json.dumps({"error": "Projeto não encontrado"}, indent=2)
            
            # Carregar projeto
            with open(project_file, "r") as f:
                project = json.load(f)
            
            # Atualizar campos
            if name:
                project["name"] = name
            
            if description:
                project["description"] = description
            
            if status:
                project["status"] = status
            
            if metadata_json:
                try:
                    metadata = json.loads(metadata_json)
                    project["metadata"].update(metadata)
                except:
                    pass
            
            # Atualizar timestamp
            project["updated_at"] = datetime.now().isoformat()
            
            # Salvar projeto
            with open(project_file, "w") as f:
                json.dump(project, f, indent=2)
            
            return json.dumps(project, indent=2)
    
    def _register_context_tools(self):
        """Registra ferramentas relacionadas a contexto"""
        
        @self.mcp.tool()
        def context_get(project_id: str) -> str:
            """
            Recupera o contexto de um projeto
            
            Args:
                project_id: ID único do projeto
            """
            logger.info(f"Recuperando contexto do projeto: {project_id}")
            
            project_file = os.path.join(PROJECTS_DIR, f"{project_id}.json")
            if not os.path.exists(project_file):
                logger.error(f"Projeto não encontrado: {project_id}")
                return json.dumps({"error": "Projeto não encontrado"}, indent=2)
            
            # Carregar projeto
            with open(project_file, "r") as f:
                project = json.load(f)
            
            # Carregar sessões
            sessions = []
            sessions_dir = os.path.join(SESSIONS_DIR, project_id)
            if os.path.exists(sessions_dir):
                for session_file in os.listdir(sessions_dir):
                    if session_file.endswith(".json"):
                        with open(os.path.join(sessions_dir, session_file), "r") as f:
                            session = json.load(f)
                            sessions.append(session)
            
            # Carregar artefatos
            artifacts = []
            artifacts_dir = os.path.join(ARTIFACTS_DIR, project_id)
            if os.path.exists(artifacts_dir):
                for artifact_file in os.listdir(artifacts_dir):
                    if artifact_file.endswith(".json"):
                        with open(os.path.join(artifacts_dir, artifact_file), "r") as f:
                            artifact = json.load(f)
                            artifacts.append(artifact)
            
            # Construir contexto completo
            context = {
                "project": project,
                "sessions": sessions,
                "artifacts": artifacts
            }
            
            return json.dumps(context, indent=2)
        
        @self.mcp.tool()
        def context_add(project_id: str, content: str, content_type: str, metadata_json: str = "{}") -> str:
            """
            Adiciona novo contexto a um projeto
            
            Args:
                project_id: ID único do projeto
                content: Conteúdo a ser adicionado
                content_type: Tipo de conteúdo (note, decision, reference, etc.)
                metadata_json: Metadados adicionais em formato JSON (opcional)
            """
            logger.info(f"Adicionando contexto ao projeto: {project_id}")
            
            project_file = os.path.join(PROJECTS_DIR, f"{project_id}.json")
            if not os.path.exists(project_file):
                logger.error(f"Projeto não encontrado: {project_id}")
                return json.dumps({"error": "Projeto não encontrado"}, indent=2)
            
            # Parsear metadados
            try:
                metadata = json.loads(metadata_json)
            except:
                metadata = {}
            
            # Criar artefato
            artifact_id = str(uuid.uuid4())
            artifact = {
                "artifact_id": artifact_id,
                "project_id": project_id,
                "content": content,
                "content_type": content_type,
                "created_at": datetime.now().isoformat(),
                "metadata": metadata
            }
            
            # Salvar artefato
            artifact_file = os.path.join(ARTIFACTS_DIR, project_id, f"{artifact_id}.json")
            os.makedirs(os.path.dirname(artifact_file), exist_ok=True)
            with open(artifact_file, "w") as f:
                json.dump(artifact, f, indent=2)
            
            # Atualizar timestamp do projeto
            with open(project_file, "r") as f:
                project = json.load(f)
            
            project["updated_at"] = datetime.now().isoformat()
            
            with open(project_file, "w") as f:
                json.dump(project, f, indent=2)
            
            return json.dumps(artifact, indent=2)
    
    def _register_session_tools(self):
        """Registra ferramentas relacionadas a sessões"""
        
        @self.mcp.tool()
        def session_start(project_id: str, agent_id: str = None, metadata_json: str = "{}") -> str:
            """
            Inicia uma nova sessão de trabalho
            
            Args:
                project_id: ID único do projeto
                agent_id: ID do agente que está iniciando a sessão (opcional)
                metadata_json: Metadados adicionais em formato JSON (opcional)
            """
            logger.info(f"Iniciando sessão para o projeto: {project_id}")
            
            project_file = os.path.join(PROJECTS_DIR, f"{project_id}.json")
            if not os.path.exists(project_file):
                logger.error(f"Projeto não encontrado: {project_id}")
                return json.dumps({"error": "Projeto não encontrado"}, indent=2)
            
            # Parsear metadados
            try:
                metadata = json.loads(metadata_json)
            except:
                metadata = {}
            
            # Criar sessão
            session_id = str(uuid.uuid4())
            session = {
                "session_id": session_id,
                "project_id": project_id,
                "agent_id": agent_id,
                "started_at": datetime.now().isoformat(),
                "ended_at": None,
                "status": "active",
                "metadata": metadata,
                "events": [
                    {
                        "event_type": "session_start",
                        "timestamp": datetime.now().isoformat(),
                        "data": {
                            "agent_id": agent_id
                        }
                    }
                ]
            }
            
            # Salvar sessão
            session_file = os.path.join(SESSIONS_DIR, project_id, f"{session_id}.json")
            os.makedirs(os.path.dirname(session_file), exist_ok=True)
            with open(session_file, "w") as f:
                json.dump(session, f, indent=2)
            
            # Atualizar timestamp do projeto
            with open(project_file, "r") as f:
                project = json.load(f)
            
            project["updated_at"] = datetime.now().isoformat()
            
            with open(project_file, "w") as f:
                json.dump(project, f, indent=2)
            
            return json.dumps(session, indent=2)
        
        @self.mcp.tool()
        def session_end(project_id: str, session_id: str, summary: str = None, metadata_json: str = "{}") -> str:
            """
            Finaliza uma sessão de trabalho
            
            Args:
                project_id: ID único do projeto
                session_id: ID da sessão
                summary: Resumo da sessão (opcional)
                metadata_json: Metadados adicionais em formato JSON (opcional)
            """
            logger.info(f"Finalizando sessão: {session_id}")
            
            session_file = os.path.join(SESSIONS_DIR, project_id, f"{session_id}.json")
            if not os.path.exists(session_file):
                logger.error(f"Sessão não encontrada: {session_id}")
                return json.dumps({"error": "Sessão não encontrada"}, indent=2)
            
            # Carregar sessão
            with open(session_file, "r") as f:
                session = json.load(f)
            
            # Parsear metadados
            try:
                metadata = json.loads(metadata_json)
            except:
                metadata = {}
            
            # Atualizar sessão
            session["ended_at"] = datetime.now().isoformat()
            session["status"] = "completed"
            session["metadata"].update(metadata)
            session["events"].append({
                "event_type": "session_end",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "summary": summary
                }
            })
            
            # Salvar sessão
            with open(session_file, "w") as f:
                json.dump(session, f, indent=2)
            
            # Atualizar timestamp do projeto
            project_file = os.path.join(PROJECTS_DIR, f"{project_id}.json")
            with open(project_file, "r") as f:
                project = json.load(f)
            
            project["updated_at"] = datetime.now().isoformat()
            
            with open(project_file, "w") as f:
                json.dump(project, f, indent=2)
            
            return json.dumps(session, indent=2)
        
        @self.mcp.tool()
        def session_add_event(project_id: str, session_id: str, event_type: str, event_data_json: str = "{}") -> str:
            """
            Adiciona um evento a uma sessão
            
            Args:
                project_id: ID único do projeto
                session_id: ID da sessão
                event_type: Tipo de evento
                event_data_json: Dados do evento em formato JSON (opcional)
            """
            logger.info(f"Adicionando evento à sessão: {session_id}")
            
            session_file = os.path.join(SESSIONS_DIR, project_id, f"{session_id}.json")
            if not os.path.exists(session_file):
                logger.error(f"Sessão não encontrada: {session_id}")
                return json.dumps({"error": "Sessão não encontrada"}, indent=2)
            
            # Carregar sessão
            with open(session_file, "r") as f:
                session = json.load(f)
            
            # Parsear dados do evento
            try:
                event_data = json.loads(event_data_json)
            except:
                event_data = {}
            
            # Adicionar evento
            session["events"].append({
                "event_type": event_type,
                "timestamp": datetime.now().isoformat(),
                "data": event_data
            })
            
            # Salvar sessão
            with open(session_file, "w") as f:
                json.dump(session, f, indent=2)
            
            return json.dumps(session, indent=2)
    
    def _register_artifact_tools(self):
        """Registra ferramentas relacionadas a artefatos"""
        
        @self.mcp.tool()
        def artifact_list(project_id: str) -> str:
            """
            Lista todos os artefatos de um projeto
            
            Args:
                project_id: ID único do projeto
            """
            logger.info(f"Listando artefatos do projeto: {project_id}")
            
            project_file = os.path.join(PROJECTS_DIR, f"{project_id}.json")
            if not os.path.exists(project_file):
                logger.error(f"Projeto não encontrado: {project_id}")
                return json.dumps({"error": "Projeto não encontrado"}, indent=2)
            
            # Listar artefatos
            artifacts = []
            artifacts_dir = os.path.join(ARTIFACTS_DIR, project_id)
            if os.path.exists(artifacts_dir):
                for artifact_file in os.listdir(artifacts_dir):
                    if artifact_file.endswith(".json"):
                        with open(os.path.join(artifacts_dir, artifact_file), "r") as f:
                            artifact = json.load(f)
                            artifacts.append({
                                "artifact_id": artifact["artifact_id"],
                                "content_type": artifact["content_type"],
                                "created_at": artifact["created_at"]
                            })
            
            return json.dumps({"artifacts": artifacts}, indent=2)
        
        @self.mcp.tool()
        def artifact_get(project_id: str, artifact_id: str) -> str:
            """
            Recupera um artefato específico
            
            Args:
                project_id: ID único do projeto
                artifact_id: ID do artefato
            """
            logger.info(f"Recuperando artefato: {artifact_id}")
            
            artifact_file = os.path.join(ARTIFACTS_DIR, project_id, f"{artifact_id}.json")
            if not os.path.exists(artifact_file):
                logger.error(f"Artefato não encontrado: {artifact_id}")
                return json.dumps({"error": "Artefato não encontrado"}, indent=2)
            
            # Carregar artefato
            with open(artifact_file, "r") as f:
                artifact = json.load(f)
            
            return json.dumps(artifact, indent=2)
        
        @self.mcp.tool()
        def artifact_create(project_id: str, content: str, content_type: str, 
                            name: str = None, metadata_json: str = "{}") -> str:
            """
            Cria um novo artefato
            
            Args:
                project_id: ID único do projeto
                content: Conteúdo do artefato
                content_type: Tipo de conteúdo (code, document, image, etc.)
                name: Nome do artefato (opcional)
                metadata_json: Metadados adicionais em formato JSON (opcional)
            """
            logger.info(f"Criando artefato para o projeto: {project_id}")
            
            project_file = os.path.join(PROJECTS_DIR, f"{project_id}.json")
            if not os.path.exists(project_file):
                logger.error(f"Projeto não encontrado: {project_id}")
                return json.dumps({"error": "Projeto não encontrado"}, indent=2)
            
            # Parsear metadados
            try:
                metadata = json.loads(metadata_json)
            except:
                metadata = {}
            
            # Criar artefato
            artifact_id = str(uuid.uuid4())
            artifact = {
                "artifact_id": artifact_id,
                "project_id": project_id,
                "name": name,
                "content": content,
                "content_type": content_type,
                "created_at": datetime.now().isoformat(),
                "metadata": metadata
            }
            
            # Salvar artefato
            artifact_file = os.path.join(ARTIFACTS_DIR, project_id, f"{artifact_id}.json")
            os.makedirs(os.path.dirname(artifact_file), exist_ok=True)
            with open(artifact_file, "w") as f:
                json.dump(artifact, f, indent=2)
            
            # Atualizar timestamp do projeto
            with open(project_file, "r") as f:
                project = json.load(f)
            
            project["updated_at"] = datetime.now().isoformat()
            
            with open(project_file, "w") as f:
                json.dump(project, f, indent=2)
            
            return json.dumps(artifact, indent=2)
    
    def run(self) -> None:
        """Executa o servidor MCP"""
        try:
            logger.info("Iniciando servidor")
            print("Iniciando Continuity Protocol Server...")
            self.mcp.run()
        except KeyboardInterrupt:
            logger.info("Servidor interrompido pelo usuário")
            print("\nServidor interrompido pelo usuário")
        except Exception as e:
            logger.error(f"Erro ao executar servidor: {str(e)}")
            print(f"ERRO: {str(e)}")

if __name__ == "__main__":
    # Criar diretórios necessários
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    
    # Criar e executar servidor
    server = ContinuityProtocolServer()
    server.run()