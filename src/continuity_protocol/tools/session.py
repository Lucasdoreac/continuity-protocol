"""
Session management tools for Continuity Protocol.

This module provides tools for creating, saving, and restoring session state,
enabling conversation continuity across different interactions.
"""

from typing import Dict, Any, Optional, List, Union
import json
import os
import uuid
import logging
from datetime import datetime
import shutil

# Configure logging
logger = logging.getLogger("continuity-protocol.session")

# Base directory for session storage
SESSIONS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))), "data", "sessions")

# Ensure sessions directory exists
os.makedirs(SESSIONS_DIR, exist_ok=True)

def session_create(name: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create a new continuity session.
    
    Args:
        name: Name of the session
        metadata: Additional metadata for the session
        
    Returns:
        Dictionary with session_id and created_at timestamp
    """
    session_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()
    
    # Initialize session data
    session_data = {
        "session_id": session_id,
        "name": name,
        "created_at": created_at,
        "updated_at": created_at,
        "metadata": metadata or {},
        "versions": []
    }
    
    # Create session directory
    session_dir = os.path.join(SESSIONS_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    # Save session metadata
    metadata_path = os.path.join(session_dir, "metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump(session_data, f, indent=2)
    
    logger.info(f"Created new session: {session_id} - {name}")
    
    return {
        "session_id": session_id,
        "created_at": created_at
    }

def session_save(session_id: str, content: Dict[str, Any], compression_level: int = 0) -> Dict[str, Any]:
    """
    Save the current state of a session.
    
    Args:
        session_id: Session identifier
        content: Session content to save
        compression_level: Compression level (0=none, 3=maximum)
        
    Returns:
        Dictionary with success status, version number, and saved_at timestamp
    """
    # Validate session exists
    session_dir = os.path.join(SESSIONS_DIR, session_id)
    metadata_path = os.path.join(session_dir, "metadata.json")
    
    if not os.path.exists(metadata_path):
        logger.error(f"Session not found: {session_id}")
        return {
            "success": False,
            "error": f"Session not found: {session_id}"
        }
    
    # Load session metadata
    with open(metadata_path, 'r') as f:
        session_data = json.load(f)
    
    # Create new version
    saved_at = datetime.now().isoformat()
    version = len(session_data["versions"]) + 1
    
    # Apply compression if needed
    compressed_content = content
    if compression_level > 0:
        # This is a placeholder for actual compression
        # In a real implementation, we would use a compression algorithm
        compressed_content = {
            "_compression_info": {
                "level": compression_level,
                "algorithm": "placeholder",
                "original_size": len(json.dumps(content))
            },
            "data": content
        }
    
    # Add version to metadata
    version_data = {
        "version": version,
        "saved_at": saved_at,
        "compression_level": compression_level,
        "size": len(json.dumps(compressed_content))
    }
    
    session_data["versions"].append(version_data)
    session_data["updated_at"] = saved_at
    
    # Save version content
    version_path = os.path.join(session_dir, f"version_{version}.json")
    with open(version_path, 'w') as f:
        json.dump(compressed_content, f, indent=2)
    
    # Update metadata
    with open(metadata_path, 'w') as f:
        json.dump(session_data, f, indent=2)
    
    logger.info(f"Saved session {session_id} - version {version}")
    
    return {
        "success": True,
        "version": version,
        "saved_at": saved_at
    }

def session_restore(session_id: str, version: Optional[int] = None) -> Dict[str, Any]:
    """
    Restore a previously saved session.
    
    Args:
        session_id: Session identifier
        version: Specific version to restore (optional)
        
    Returns:
        Dictionary with success status, restored content, metadata, and version
    """
    # Validate session exists
    session_dir = os.path.join(SESSIONS_DIR, session_id)
    metadata_path = os.path.join(session_dir, "metadata.json")
    
    if not os.path.exists(metadata_path):
        logger.error(f"Session not found: {session_id}")
        return {
            "success": False,
            "error": f"Session not found: {session_id}"
        }
    
    # Load session metadata
    with open(metadata_path, 'r') as f:
        session_data = json.load(f)
    
    if not session_data["versions"]:
        logger.error(f"No versions found for session: {session_id}")
        return {
            "success": False,
            "error": f"No versions found for session: {session_id}"
        }
    
    # Determine which version to restore
    target_version = version
    if target_version is None:
        # Use latest version
        target_version = session_data["versions"][-1]["version"]
    
    # Find version data
    version_data = next((v for v in session_data["versions"] if v["version"] == target_version), None)
    if version_data is None:
        logger.error(f"Version {version} not found for session: {session_id}")
        return {
            "success": False,
            "error": f"Version {version} not found for session: {session_id}"
        }
    
    # Load version content
    version_path = os.path.join(session_dir, f"version_{target_version}.json")
    if not os.path.exists(version_path):
        logger.error(f"Version file not found: {version_path}")
        return {
            "success": False,
            "error": f"Version file not found for version {target_version}"
        }
    
    with open(version_path, 'r') as f:
        content = json.load(f)
    
    # Decompress if needed
    if version_data.get("compression_level", 0) > 0:
        # This is a placeholder for actual decompression
        # In a real implementation, we would use a decompression algorithm
        if "_compression_info" in content:
            content = content.get("data", {})
    
    logger.info(f"Restored session {session_id} - version {target_version}")
    
    return {
        "success": True,
        "content": content,
        "metadata": session_data["metadata"],
        "version": target_version
    }

def session_list() -> Dict[str, Any]:
    """
    List all available sessions.
    
    Returns:
        Dictionary with list of sessions and their basic metadata
    """
    sessions = []
    
    # Iterate through session directories
    for session_id in os.listdir(SESSIONS_DIR):
        session_dir = os.path.join(SESSIONS_DIR, session_id)
        
        # Skip if not a directory
        if not os.path.isdir(session_dir):
            continue
        
        # Check for metadata file
        metadata_path = os.path.join(session_dir, "metadata.json")
        if not os.path.exists(metadata_path):
            continue
        
        # Load session metadata
        try:
            with open(metadata_path, 'r') as f:
                session_data = json.load(f)
            
            # Add basic session info to list
            sessions.append({
                "session_id": session_data["session_id"],
                "name": session_data["name"],
                "created_at": session_data["created_at"],
                "updated_at": session_data["updated_at"],
                "versions": len(session_data["versions"])
            })
        except Exception as e:
            logger.error(f"Error loading session {session_id}: {str(e)}")
    
    logger.info(f"Listed {len(sessions)} sessions")
    
    return {
        "success": True,
        "sessions": sessions,
        "count": len(sessions)
    }

def session_delete(session_id: str) -> Dict[str, Any]:
    """
    Delete a session and all its versions.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Dictionary with success status
    """
    # Validate session exists
    session_dir = os.path.join(SESSIONS_DIR, session_id)
    
    if not os.path.exists(session_dir):
        logger.error(f"Session not found: {session_id}")
        return {
            "success": False,
            "error": f"Session not found: {session_id}"
        }
    
    # Delete session directory
    try:
        shutil.rmtree(session_dir)
        logger.info(f"Deleted session: {session_id}")
        
        return {
            "success": True,
            "session_id": session_id
        }
    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {str(e)}")
        return {
            "success": False,
            "error": f"Error deleting session: {str(e)}"
        }

def session_update_metadata(session_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update session metadata.
    
    Args:
        session_id: Session identifier
        metadata: New metadata
        
    Returns:
        Dictionary with success status
    """
    # Validate session exists
    session_dir = os.path.join(SESSIONS_DIR, session_id)
    metadata_path = os.path.join(session_dir, "metadata.json")
    
    if not os.path.exists(metadata_path):
        logger.error(f"Session not found: {session_id}")
        return {
            "success": False,
            "error": f"Session not found: {session_id}"
        }
    
    # Load session metadata
    with open(metadata_path, 'r') as f:
        session_data = json.load(f)
    
    # Update metadata
    session_data["metadata"].update(metadata)
    session_data["updated_at"] = datetime.now().isoformat()
    
    # Save updated metadata
    with open(metadata_path, 'w') as f:
        json.dump(session_data, f, indent=2)
    
    logger.info(f"Updated metadata for session: {session_id}")
    
    return {
        "success": True,
        "session_id": session_id,
        "updated_at": session_data["updated_at"]
    }