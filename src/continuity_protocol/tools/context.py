"""
Context management tools for Continuity Protocol.

This module provides tools for storing, retrieving, and manipulating context
information, enabling seamless context preservation and switching.

Contexts are now stored within project directories, identified by project IDs,
ensuring complete separation between the protocol and project-specific data.
"""

from typing import Dict, Any, Optional, List, Union
import json
import os
import logging
from datetime import datetime, timedelta
import time
import hashlib

from ..project_id import (
    ProjectRegistry, ProjectContext,
    get_current_project_id, ensure_project_context
)

# Configure logging
logger = logging.getLogger("continuity-protocol.context")

# Legacy base directory for context storage (used as fallback)
LEGACY_CONTEXTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))), "data", "contexts")

# Default namespace
DEFAULT_NAMESPACE = "default"

# Ensure legacy contexts directory exists for backward compatibility
os.makedirs(LEGACY_CONTEXTS_DIR, exist_ok=True)

def _get_context_path(key: str, namespace: str = DEFAULT_NAMESPACE, project_id: Optional[str] = None) -> str:
    """
    Get the path for a context file

    Args:
        key: Context identifier key
        namespace: Context namespace
        project_id: Optional project ID (if None, uses current project or legacy path)

    Returns:
        str: Path to context file
    """
    # Sanitize key for use in filenames
    safe_key = hashlib.md5(key.encode()).hexdigest()

    # Try to use project-specific context if project_id is provided or can be detected
    if project_id is None:
        project_id = get_current_project_id()

    if project_id:
        try:
            # Use project-specific context directory
            project_context = ProjectContext(project_id)
            return project_context.get_context_path(key, namespace)
        except Exception as e:
            logger.error(f"Error getting project context path: {e}")
            # Fall back to legacy path

    # Use legacy path (backward compatibility)
    namespace_dir = os.path.join(LEGACY_CONTEXTS_DIR, namespace)
    os.makedirs(namespace_dir, exist_ok=True)

    return os.path.join(namespace_dir, f"{safe_key}.json")

def context_store(key: str, value: Any, ttl: Optional[int] = None,
                  namespace: str = DEFAULT_NAMESPACE,
                  project_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Store context information.

    Args:
        key: Context identifier key
        value: Context value to store
        ttl: Time to live in seconds (optional)
        namespace: Context namespace (optional)
        project_id: Project ID to store context for (optional, uses current project if not specified)

    Returns:
        Dictionary with success status and expiration time if TTL was specified
    """
    # Calculate expiration time if TTL is specified
    expires_at = None
    if ttl is not None:
        expires_at = (datetime.now() + timedelta(seconds=ttl)).isoformat()
    
    # Create context data
    context_data = {
        "key": key,
        "value": value,
        "stored_at": datetime.now().isoformat(),
        "expires_at": expires_at,
        "namespace": namespace
    }
    
    # Get context file path
    context_path = _get_context_path(key, namespace, project_id)
    
    # Save context data
    try:
        with open(context_path, 'w') as f:
            json.dump(context_data, f, indent=2)
        
        logger.info(f"Stored context: {namespace}/{key}")
        
        return {
            "success": True,
            "expires_at": expires_at
        }
    except Exception as e:
        logger.error(f"Error storing context {namespace}/{key}: {str(e)}")
        return {
            "success": False,
            "error": f"Error storing context: {str(e)}"
        }

def context_retrieve(key: str, namespace: str = DEFAULT_NAMESPACE, project_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve stored context information.

    Args:
        key: Context identifier key
        namespace: Context namespace (optional)
        project_id: Project ID to retrieve context from (optional, uses current project if not specified)

    Returns:
        Dictionary with success status and retrieved context value
    """
    # Get context file path
    context_path = _get_context_path(key, namespace, project_id)
    
    # Check if context file exists
    if not os.path.exists(context_path):
        logger.error(f"Context not found: {namespace}/{key}")
        return {
            "success": False,
            "error": f"Context not found: {namespace}/{key}"
        }
    
    # Load context data
    try:
        with open(context_path, 'r') as f:
            context_data = json.load(f)
        
        # Check if context has expired
        if context_data.get("expires_at"):
            expires_at = datetime.fromisoformat(context_data["expires_at"])
            if datetime.now() > expires_at:
                logger.warning(f"Context {namespace}/{key} has expired")
                
                # Delete expired context
                os.remove(context_path)
                
                return {
                    "success": False,
                    "error": f"Context has expired",
                    "stored_at": context_data["stored_at"],
                    "expired_at": context_data["expires_at"]
                }
        
        logger.info(f"Retrieved context: {namespace}/{key}")
        
        return {
            "success": True,
            "value": context_data["value"],
            "stored_at": context_data["stored_at"],
            "expires_at": context_data.get("expires_at")
        }
    except Exception as e:
        logger.error(f"Error retrieving context {namespace}/{key}: {str(e)}")
        return {
            "success": False,
            "error": f"Error retrieving context: {str(e)}"
        }

def context_switch(target_context: str, preserve_current: bool = True) -> Dict[str, Any]:
    """
    Switch between different contexts.
    
    Args:
        target_context: Target context identifier
        preserve_current: Whether to preserve current context for later restoration
        
    Returns:
        Dictionary with success status and previous context information
    """
    # Get current active context
    active_context_path = os.path.join(CONTEXTS_DIR, "active_context.json")
    previous_context = None
    
    # Check if there is an active context
    if os.path.exists(active_context_path):
        try:
            with open(active_context_path, 'r') as f:
                previous_context = json.load(f)
            
            if preserve_current:
                # Store the current context for later restoration
                # This is a simplified implementation - in a real system, 
                # we would need to store the full context state
                context_store(
                    key=f"_prev_{int(time.time())}",
                    value={
                        "context_id": previous_context["context_id"],
                        "switched_at": previous_context["switched_at"]
                    },
                    namespace="_context_history"
                )
        except Exception as e:
            logger.error(f"Error reading active context: {str(e)}")
    
    # Set new active context
    try:
        active_context = {
            "context_id": target_context,
            "switched_at": datetime.now().isoformat(),
            "previous_context": previous_context["context_id"] if previous_context else None
        }
        
        with open(active_context_path, 'w') as f:
            json.dump(active_context, f, indent=2)
        
        logger.info(f"Switched to context: {target_context}")
        
        # Load the target context
        # This is a placeholder - in a real implementation, we would load
        # the actual context state here
        context_loaded = True
        
        return {
            "success": True,
            "previous_context": previous_context["context_id"] if previous_context else None,
            "context_loaded": context_loaded
        }
    except Exception as e:
        logger.error(f"Error switching context: {str(e)}")
        return {
            "success": False,
            "error": f"Error switching context: {str(e)}"
        }

def context_delete(key: str, namespace: str = DEFAULT_NAMESPACE, project_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Delete stored context information.

    Args:
        key: Context identifier key
        namespace: Context namespace (optional)
        project_id: Project ID to delete context from (optional, uses current project if not specified)

    Returns:
        Dictionary with success status
    """
    # Get context file path
    context_path = _get_context_path(key, namespace, project_id)
    
    # Check if context file exists
    if not os.path.exists(context_path):
        logger.error(f"Context not found: {namespace}/{key}")
        return {
            "success": False,
            "error": f"Context not found: {namespace}/{key}"
        }
    
    # Delete context file
    try:
        os.remove(context_path)
        logger.info(f"Deleted context: {namespace}/{key}")
        
        return {
            "success": True,
            "key": key,
            "namespace": namespace
        }
    except Exception as e:
        logger.error(f"Error deleting context {namespace}/{key}: {str(e)}")
        return {
            "success": False,
            "error": f"Error deleting context: {str(e)}"
        }

def context_list(namespace: str = DEFAULT_NAMESPACE, include_expired: bool = False, project_id: Optional[str] = None) -> Dict[str, Any]:
    """
    List stored context information in a namespace.

    Args:
        namespace: Context namespace (optional)
        include_expired: Whether to include expired contexts (optional)
        project_id: Project ID to list contexts from (optional, uses current project if not specified)

    Returns:
        Dictionary with success status and list of contexts
    """
    # Try to use project-specific context directory if project_id is provided or can be detected
    if project_id is None:
        project_id = get_current_project_id()

    if project_id:
        try:
            # Use project-specific context directory
            project_context = ProjectContext(project_id)
            namespace_dir = os.path.join(project_context.contexts_dir, namespace)
        except Exception as e:
            logger.error(f"Error getting project context directory: {e}")
            # Fall back to legacy path
            namespace_dir = os.path.join(LEGACY_CONTEXTS_DIR, namespace)
    else:
        # Use legacy path
        namespace_dir = os.path.join(LEGACY_CONTEXTS_DIR, namespace)

    # Check if namespace directory exists
    if not os.path.exists(namespace_dir):
        logger.warning(f"Namespace not found: {namespace} for project: {project_id or 'legacy'}")
        return {
            "success": True,
            "contexts": [],
            "count": 0
        }
    
    # List context files
    contexts = []
    try:
        for filename in os.listdir(namespace_dir):
            if not filename.endswith(".json"):
                continue
            
            context_path = os.path.join(namespace_dir, filename)
            
            try:
                with open(context_path, 'r') as f:
                    context_data = json.load(f)
                
                # Check if context has expired
                if not include_expired and context_data.get("expires_at"):
                    expires_at = datetime.fromisoformat(context_data["expires_at"])
                    if datetime.now() > expires_at:
                        continue
                
                # Add context to list
                contexts.append({
                    "key": context_data["key"],
                    "stored_at": context_data["stored_at"],
                    "expires_at": context_data.get("expires_at")
                })
            except Exception as e:
                logger.error(f"Error reading context file {filename}: {str(e)}")
        
        logger.info(f"Listed {len(contexts)} contexts in namespace {namespace}")
        
        return {
            "success": True,
            "contexts": contexts,
            "count": len(contexts)
        }
    except Exception as e:
        logger.error(f"Error listing contexts in namespace {namespace}: {str(e)}")
        return {
            "success": False,
            "error": f"Error listing contexts: {str(e)}"
        }