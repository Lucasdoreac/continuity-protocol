"""
Project management tools for the Continuity Protocol.

These tools allow working with project identifiers, providing a clean
separation between the protocol infrastructure and specific project data.
"""

import os
import json
from typing import Dict, Any, Optional, List

from ..project_id import (
    ProjectRegistry, ProjectContext, 
    get_current_project_id, ensure_project_context
)

def project_register(
    name: str,
    directory: Optional[str] = None,
    description: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Register a new project or update an existing one.
    
    Args:
        name: Human-readable project name
        directory: Project directory (default: current working directory)
        description: Optional project description
        metadata: Optional additional metadata
    
    Returns:
        Dict: Result with project_id and success status
    """
    try:
        if directory is None:
            directory = os.getcwd()
        
        registry = ProjectRegistry()
        project_id = registry.register_project(
            name=name,
            directory=directory,
            description=description,
            metadata=metadata
        )
        
        return {
            "success": True,
            "project_id": project_id,
            "name": name,
            "directory": directory
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def project_get(project_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get project information.
    
    Args:
        project_id: Project ID (default: current project)
    
    Returns:
        Dict: Result with project information or error
    """
    try:
        registry = ProjectRegistry()
        
        if project_id is None:
            project_id = get_current_project_id()
            if project_id is None:
                return {
                    "success": False,
                    "error": "No project ID specified and no current project found"
                }
        
        project_data = registry.get_project(project_id)
        if project_data is None:
            return {
                "success": False,
                "error": f"Project with ID {project_id} not found"
            }
        
        return {
            "success": True,
            "project_id": project_id,
            **project_data
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def project_list() -> Dict[str, Any]:
    """
    List all registered projects.
    
    Returns:
        Dict: Result with list of projects
    """
    try:
        registry = ProjectRegistry()
        projects = registry.get_all_projects()
        
        return {
            "success": True,
            "count": len(projects),
            "projects": projects
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def project_unregister(project_id: str) -> Dict[str, Any]:
    """
    Unregister a project.
    
    Args:
        project_id: Project ID to unregister
    
    Returns:
        Dict: Result with success status
    """
    try:
        registry = ProjectRegistry()
        
        # Get project data before unregistering
        project_data = registry.get_project(project_id)
        if project_data is None:
            return {
                "success": False,
                "error": f"Project with ID {project_id} not found"
            }
        
        success = registry.unregister_project(project_id)
        
        return {
            "success": success,
            "project_id": project_id,
            "name": project_data["name"],
            "message": f"Project '{project_data['name']}' unregistered"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def project_set_current(
    project_id: Optional[str] = None,
    directory: Optional[str] = None
) -> Dict[str, Any]:
    """
    Set the current project by ID or directory.
    
    Args:
        project_id: Project ID to set as current
        directory: Project directory to set as current
    
    Returns:
        Dict: Result with success status and project information
    """
    try:
        registry = ProjectRegistry()
        
        if project_id is not None:
            # Set by project ID
            project_data = registry.get_project(project_id)
            if project_data is None:
                return {
                    "success": False,
                    "error": f"Project with ID {project_id} not found"
                }
            
            # Create an environment variable or file in home directory
            # to store the current project ID
            current_file = os.path.join(registry.registry_dir, "current_project")
            with open(current_file, 'w') as f:
                f.write(project_id)
            
            return {
                "success": True,
                "project_id": project_id,
                "name": project_data["name"],
                "directory": project_data["directory"],
                "message": f"Current project set to '{project_data['name']}'"
            }
        
        elif directory is not None:
            # Set by directory
            project_id = registry.find_project_by_directory(directory)
            if project_id is None:
                return {
                    "success": False,
                    "error": f"No project found for directory {directory}"
                }
            
            # Recursively call with found project_id
            return project_set_current(project_id=project_id)
        
        else:
            return {
                "success": False,
                "error": "Either project_id or directory must be specified"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def project_get_current() -> Dict[str, Any]:
    """
    Get the current project.
    
    Returns:
        Dict: Result with current project information or error
    """
    try:
        # Try to get current project ID
        project_id = get_current_project_id()
        if project_id is None:
            # Check if there's a current project file
            registry = ProjectRegistry()
            current_file = os.path.join(registry.registry_dir, "current_project")
            if os.path.exists(current_file):
                with open(current_file, 'r') as f:
                    project_id = f.read().strip()
        
        if project_id is None:
            return {
                "success": False,
                "error": "No current project set"
            }
        
        # Get project data
        return project_get(project_id)
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }