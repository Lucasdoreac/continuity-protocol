"""
Project ID Management for Continuity Protocol

This module handles the abstraction of project identifiers, providing a clean
separation between the Continuity Protocol infrastructure and specific project data.
"""

import os
import json
import uuid
from typing import Dict, Any, Optional, List
from pathlib import Path

class ProjectRegistry:
    """Registry for managing project identifiers and metadata."""
    
    def __init__(self, registry_path: Optional[str] = None):
        """
        Initialize the project registry.
        
        Args:
            registry_path: Path to the registry file. If None, uses default location.
        """
        if registry_path is None:
            # Use default location in user's home directory to avoid storing in repo
            home_dir = os.path.expanduser("~")
            self.registry_dir = os.path.join(home_dir, ".continuity")
            os.makedirs(self.registry_dir, exist_ok=True)
            self.registry_path = os.path.join(self.registry_dir, "project_registry.json")
        else:
            self.registry_path = registry_path
            self.registry_dir = os.path.dirname(registry_path)
            os.makedirs(self.registry_dir, exist_ok=True)
        
        # Initialize or load registry
        self.registry = self._load_registry()
    
    def _load_registry(self) -> Dict[str, Any]:
        """Load the project registry from disk."""
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # If file is corrupted or cannot be read, create a new registry
                return {"projects": {}, "version": "1.0"}
        else:
            # Create a new registry if it doesn't exist
            return {"projects": {}, "version": "1.0"}
    
    def _save_registry(self) -> None:
        """Save the project registry to disk."""
        with open(self.registry_path, 'w') as f:
            json.dump(self.registry, f, indent=2)
    
    def register_project(self, 
                        name: str, 
                        directory: str, 
                        description: Optional[str] = None, 
                        metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Register a new project or update an existing one.
        
        Args:
            name: Human-readable project name
            directory: Absolute path to project directory
            description: Optional project description
            metadata: Optional additional metadata
            
        Returns:
            str: Project ID (UUID)
        """
        # Check if project with this directory already exists
        for project_id, project_data in self.registry["projects"].items():
            if project_data["directory"] == directory:
                # Update existing project
                project_data["name"] = name
                if description is not None:
                    project_data["description"] = description
                if metadata is not None:
                    project_data["metadata"].update(metadata)
                self._save_registry()
                return project_id
        
        # Create new project ID (UUID v4)
        project_id = str(uuid.uuid4())
        
        # Add to registry
        self.registry["projects"][project_id] = {
            "name": name,
            "directory": directory,
            "description": description or "",
            "registered_at": self._get_timestamp(),
            "last_accessed": self._get_timestamp(),
            "metadata": metadata or {}
        }
        
        # Save updated registry
        self._save_registry()
        
        # Create project continuity directory if it doesn't exist
        continuity_dir = os.path.join(directory, ".continuity")
        os.makedirs(continuity_dir, exist_ok=True)
        
        # Create project config file
        config = {
            "project_id": project_id,
            "name": name,
            "registered_at": self.registry["projects"][project_id]["registered_at"]
        }
        with open(os.path.join(continuity_dir, "config.json"), 'w') as f:
            json.dump(config, f, indent=2)
        
        return project_id
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get project data by ID.
        
        Args:
            project_id: Project ID to look up
            
        Returns:
            Dict or None: Project data if found, None otherwise
        """
        if project_id in self.registry["projects"]:
            # Update last accessed timestamp
            self.registry["projects"][project_id]["last_accessed"] = self._get_timestamp()
            self._save_registry()
            return self.registry["projects"][project_id]
        return None
    
    def find_project_by_directory(self, directory: str) -> Optional[str]:
        """
        Find project ID based on directory path.
        
        Args:
            directory: Directory path to search for
            
        Returns:
            str or None: Project ID if found, None otherwise
        """
        directory = os.path.abspath(directory)
        for project_id, project_data in self.registry["projects"].items():
            if project_data["directory"] == directory:
                return project_id
        return None
    
    def get_all_projects(self) -> List[Dict[str, Any]]:
        """
        Get all registered projects.
        
        Returns:
            List: List of project data dictionaries with IDs
        """
        return [
            {"project_id": project_id, **project_data}
            for project_id, project_data in self.registry["projects"].items()
        ]
    
    def unregister_project(self, project_id: str) -> bool:
        """
        Unregister a project.
        
        Args:
            project_id: Project ID to unregister
            
        Returns:
            bool: True if project was unregistered, False if not found
        """
        if project_id in self.registry["projects"]:
            del self.registry["projects"][project_id]
            self._save_registry()
            return True
        return False
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()


class ProjectContext:
    """
    Context manager for working with project-specific data.
    Ensures that data is always stored in the project's own directory.
    """
    
    def __init__(self, project_id: str, registry: Optional[ProjectRegistry] = None):
        """
        Initialize project context.
        
        Args:
            project_id: Project ID to work with
            registry: Optional project registry instance
        """
        self.project_id = project_id
        self.registry = registry or ProjectRegistry()
        self.project_data = self.registry.get_project(project_id)
        
        if self.project_data is None:
            raise ValueError(f"Project with ID {project_id} not found in registry")
        
        self.project_dir = self.project_data["directory"]
        self.continuity_dir = os.path.join(self.project_dir, ".continuity")
        
        # Ensure continuity directories exist
        self.contexts_dir = os.path.join(self.continuity_dir, "contexts")
        self.sessions_dir = os.path.join(self.continuity_dir, "sessions")
        self.data_dir = os.path.join(self.continuity_dir, "data")
        
        os.makedirs(self.contexts_dir, exist_ok=True)
        os.makedirs(self.sessions_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
    
    def get_context_path(self, context_key: str, namespace: str = "default") -> str:
        """
        Get path for storing context data.
        
        Args:
            context_key: Context identifier
            namespace: Optional namespace
            
        Returns:
            str: Absolute path for context data
        """
        namespace_dir = os.path.join(self.contexts_dir, namespace)
        os.makedirs(namespace_dir, exist_ok=True)
        return os.path.join(namespace_dir, f"{context_key}.json")
    
    def get_session_path(self, session_id: str) -> str:
        """
        Get path for storing session data.
        
        Args:
            session_id: Session identifier
            
        Returns:
            str: Absolute path for session data
        """
        session_dir = os.path.join(self.sessions_dir, session_id)
        os.makedirs(session_dir, exist_ok=True)
        return session_dir
    
    def get_data_path(self, data_type: str) -> str:
        """
        Get path for storing project-specific data.
        
        Args:
            data_type: Type of data (subfolder name)
            
        Returns:
            str: Absolute path for data
        """
        data_type_dir = os.path.join(self.data_dir, data_type)
        os.makedirs(data_type_dir, exist_ok=True)
        return data_type_dir


def get_current_project_id(directory: Optional[str] = None) -> Optional[str]:
    """
    Get the project ID for the current directory or specified directory.
    
    Args:
        directory: Directory to check (default: current working directory)
        
    Returns:
        str or None: Project ID if found, None otherwise
    """
    if directory is None:
        directory = os.getcwd()
    
    # Try finding existing project
    registry = ProjectRegistry()
    project_id = registry.find_project_by_directory(directory)
    
    if project_id:
        return project_id
        
    # Try looking for .continuity/config.json in current directory
    continuity_config = os.path.join(directory, ".continuity", "config.json")
    if os.path.exists(continuity_config):
        try:
            with open(continuity_config, 'r') as f:
                config = json.load(f)
                if "project_id" in config:
                    # Verify this ID exists in registry
                    if registry.get_project(config["project_id"]) is not None:
                        return config["project_id"]
                    
                    # If not in registry but has valid config, re-register
                    if "name" in config:
                        return registry.register_project(
                            name=config["name"],
                            directory=directory
                        )
        except (json.JSONDecodeError, IOError):
            pass
    
    return None


def ensure_project_context(directory: Optional[str] = None, 
                          name: Optional[str] = None) -> str:
    """
    Ensure that the current directory is registered as a project.
    If it's not, register it with the given name or a default name.
    
    Args:
        directory: Directory to check (default: current working directory)
        name: Project name to use if registering new project
        
    Returns:
        str: Project ID
    """
    if directory is None:
        directory = os.getcwd()
    
    # Try finding existing project
    project_id = get_current_project_id(directory)
    
    if project_id:
        return project_id
    
    # Register new project
    if name is None:
        name = os.path.basename(directory)
    
    registry = ProjectRegistry()
    return registry.register_project(
        name=name,
        directory=directory
    )