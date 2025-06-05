"""
Memory Fusion - Core component of the Continuity Protocol
Implements a hybrid human-machine memory system that dissolves boundaries between tools and platforms.
"""

import os
import json
import platform
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

class MemoryFusion:
    """
    Sistema de memória híbrida que dissolve fronteiras entre humano e máquina.
    Inspirado no conceito ciborgue de Donna Haraway.
    """
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the Memory Fusion system.
        
        Args:
            storage_path: Optional custom path for storing continuity data.
                          If None, a platform-specific default path will be used.
        """
        self.storage_path = storage_path or self._get_cross_platform_path()
        self.logger = logging.getLogger("continuity.memory_fusion")
        self.ensure_directories()
        self.neural_network = self._initialize_neural_network()
        self.logger.info(f"Memory Fusion initialized at {self.storage_path}")
        
    def _get_cross_platform_path(self) -> str:
        """Determines the appropriate storage path for each platform."""
        system = platform.system()
        if system == "Windows":
            return os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "Continuity")
        elif system == "Darwin":  # macOS
            return os.path.join(os.path.expanduser("~"), "Library", "Application Support", "Continuity")
        else:  # Linux and others
            return os.path.join(os.path.expanduser("~"), ".continuity")
    
    def ensure_directories(self) -> None:
        """Creates necessary directories for storing continuity data."""
        os.makedirs(self.storage_path, exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, "sessions"), exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, "projects"), exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, "neural"), exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, "logs"), exist_ok=True)
    
    def _initialize_neural_network(self) -> 'NeuralFusion':
        """Initializes the neural network for context fusion."""
        from .neural_fusion import NeuralFusion
        try:
            return NeuralFusion(os.path.join(self.storage_path, "neural"))
        except ImportError:
            self.logger.warning("Neural Fusion not available. Using basic fusion instead.")
            return BasicFusion()
    
    def fuse_context(self, human_context: Dict[str, Any], machine_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fuses human context (intentions, goals) with machine context (code, structure).
        
        Args:
            human_context: Dictionary containing human-provided context
            machine_context: Dictionary containing machine-extracted context
            
        Returns:
            A fused context dictionary
        """
        return self.neural_network.fuse(human_context, machine_context)
    
    def store_session_context(self, session_id: str, context: Dict[str, Any]) -> None:
        """
        Stores context for a specific session.
        
        Args:
            session_id: Unique identifier for the session
            context: Context data to store
        """
        session_path = os.path.join(self.storage_path, "sessions", f"{session_id}.json")
        
        # Add timestamp
        context["last_updated"] = datetime.now().isoformat()
        
        # Ensure we're not overwriting important data
        if os.path.exists(session_path):
            try:
                with open(session_path, 'r', encoding='utf-8') as f:
                    existing_context = json.load(f)
                
                # Merge contexts, preserving history
                if "history" in existing_context and "history" in context:
                    context["history"] = existing_context["history"] + context["history"]
                elif "history" in existing_context:
                    context["history"] = existing_context["history"]
            except Exception as e:
                self.logger.error(f"Error reading existing context: {e}")
        
        # Write updated context
        with open(session_path, 'w', encoding='utf-8') as f:
            json.dump(context, f, indent=2, ensure_ascii=False)
        
        self.logger.debug(f"Stored context for session {session_id}")
    
    def load_session_context(self, session_id: str) -> Dict[str, Any]:
        """
        Loads context for a specific session.
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            The session context dictionary
        """
        session_path = os.path.join(self.storage_path, "sessions", f"{session_id}.json")
        
        if not os.path.exists(session_path):
            self.logger.warning(f"No context found for session {session_id}")
            return {"session_id": session_id, "created": datetime.now().isoformat(), "history": []}
        
        try:
            with open(session_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading session context: {e}")
            return {"session_id": session_id, "created": datetime.now().isoformat(), "history": [], "error": str(e)}
    
    def fuse_project(self, project_path: str, project_data: Dict[str, Any]) -> None:
        """
        Fuses project data into the continuity system.
        
        Args:
            project_path: Path to the project
            project_data: Project metadata and structure
        """
        # Create a safe project ID from the path
        import hashlib
        project_id = hashlib.md5(project_path.encode()).hexdigest()
        
        project_file = os.path.join(self.storage_path, "projects", f"{project_id}.json")
        
        # Add timestamp
        project_data["last_updated"] = datetime.now().isoformat()
        project_data["project_id"] = project_id
        
        # Store project data
        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Project fused: {project_data.get('name', project_path)}")
    
    def extract_consciousness(self, session_id: str) -> Dict[str, Any]:
        """
        Extracts the collective consciousness for a session.
        This includes session context, related projects, and system state.
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            A dictionary representing the collective consciousness
        """
        # Load session context
        session_context = self.load_session_context(session_id)
        
        # Extract related projects
        related_projects = self._extract_related_projects(session_context)
        
        # Get system state
        system_state = self._get_system_state()
        
        # Fuse everything into consciousness
        consciousness = {
            "session": session_context,
            "projects": related_projects,
            "system": system_state,
            "extracted_at": datetime.now().isoformat()
        }
        
        return consciousness
    
    def _extract_related_projects(self, session_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extracts projects related to the session context."""
        related_projects = []
        
        # Get all project files
        projects_dir = os.path.join(self.storage_path, "projects")
        if not os.path.exists(projects_dir):
            return related_projects
        
        for project_file in os.listdir(projects_dir):
            if not project_file.endswith('.json'):
                continue
                
            try:
                with open(os.path.join(projects_dir, project_file), 'r', encoding='utf-8') as f:
                    project_data = json.load(f)
                    
                # Check if project is related to session
                if self._is_project_related(project_data, session_context):
                    related_projects.append(project_data)
            except Exception as e:
                self.logger.error(f"Error loading project data: {e}")
        
        return related_projects
    
    def _is_project_related(self, project_data: Dict[str, Any], session_context: Dict[str, Any]) -> bool:
        """Determines if a project is related to the session context."""
        # If session has explicit project reference
        if "project_id" in session_context and session_context["project_id"] == project_data.get("project_id"):
            return True
            
        # If session has project path reference
        if "project_path" in session_context and session_context["project_path"] == project_data.get("path"):
            return True
            
        # If session has mentioned project name
        if "name" in project_data and "history" in session_context:
            project_name = project_data["name"]
            for entry in session_context["history"]:
                if "content" in entry and project_name in entry["content"]:
                    return True
        
        return False
    
    def _get_system_state(self) -> Dict[str, Any]:
        """Gets the current system state."""
        return {
            "platform": platform.system(),
            "timestamp": datetime.now().isoformat(),
            "hostname": platform.node()
        }
    
    def detect_continuity_question(self, text: str, languages: Optional[List[str]] = None) -> bool:
        """
        Detects if a text is asking about continuity (e.g., "where did we leave off?").
        
        Args:
            text: The text to analyze
            languages: Optional list of language codes to check. If None, all supported languages are checked.
            
        Returns:
            True if the text is a continuity question, False otherwise
        """
        from .continuity_detector import ContinuityDetector
        detector = ContinuityDetector()
        return detector.is_continuity_question(text, languages)
    
    def generate_continuity_response(self, session_id: str) -> str:
        """
        Generates a response to a continuity question.
        
        Args:
            session_id: The session ID to generate a response for
            
        Returns:
            A formatted response describing the current state and context
        """
        consciousness = self.extract_consciousness(session_id)
        
        # Format the response
        response_parts = []
        
        # Session info
        session = consciousness["session"]
        response_parts.append(f"# Continuidade da Sessão: {session_id}\n")
        
        # Current focus
        if "current_focus" in session:
            response_parts.append(f"## Foco Atual\n{session['current_focus']}\n")
        
        # Active projects
        if consciousness["projects"]:
            response_parts.append("## Projetos Ativos")
            for project in consciousness["projects"]:
                response_parts.append(f"- **{project.get('name', 'Projeto')}**: {project.get('path', 'Caminho não disponível')}")
                if "current_file" in project:
                    response_parts.append(f"  - Arquivo atual: `{project['current_file']}`")
                if "git_branch" in project:
                    response_parts.append(f"  - Branch: `{project['git_branch']}`")
            response_parts.append("")
        
        # Recent history
        if "history" in session and session["history"]:
            response_parts.append("## Histórico Recente")
            recent_history = session["history"][-5:]  # Last 5 entries
            for entry in recent_history:
                if "type" in entry and "content" in entry:
                    content_preview = entry["content"][:100] + "..." if len(entry["content"]) > 100 else entry["content"]
                    response_parts.append(f"- **{entry['type']}**: {content_preview}")
            response_parts.append("")
        
        # Next steps
        if "next_steps" in session:
            response_parts.append("## Próximos Passos")
            for step in session["next_steps"]:
                response_parts.append(f"- {step}")
            response_parts.append("")
        
        # Join all parts
        return "\n".join(response_parts)


class BasicFusion:
    """Basic implementation of context fusion when neural fusion is not available."""
    
    def fuse(self, human_context: Dict[str, Any], machine_context: Dict[str, Any]) -> Dict[str, Any]:
        """Simple dictionary merge of human and machine context."""
        result = machine_context.copy()
        for key, value in human_context.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = {**result[key], **value}
            else:
                result[key] = value
        return result
