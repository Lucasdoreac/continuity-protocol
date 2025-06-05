"""
System management tools for Continuity Protocol.

This module provides tools for system status, memory optimization, and other
system-level operations.
"""

from typing import Dict, Any, Optional, List, Union, Tuple
import json
import os
import logging
import platform
import time
import psutil
from datetime import datetime, timedelta
import subprocess

# Configure logging
logger = logging.getLogger("continuity-protocol.system")

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

# Import version
from continuity_protocol import __version__

# Start time of the server
SERVER_START_TIME = datetime.now()

def system_status(include_sessions: bool = False, include_metrics: bool = False) -> Dict[str, Any]:
    """
    Get the status of the continuity system.
    
    Args:
        include_sessions: Whether to include active sessions in the response
        include_metrics: Whether to include system metrics in the response
        
    Returns:
        Dictionary with system status information
    """
    # Basic status info
    status_info = {
        "status": "healthy",  # Default status
        "version": __version__,
        "uptime_seconds": (datetime.now() - SERVER_START_TIME).total_seconds(),
        "platform": platform.platform(),
        "python_version": platform.python_version()
    }
    
    # Include active sessions if requested
    if include_sessions:
        try:
            # Import session tools
            from continuity_protocol.tools.session import session_list
            
            # Get session list
            sessions_result = session_list()
            if sessions_result["success"]:
                status_info["active_sessions"] = sessions_result["sessions"]
            else:
                status_info["active_sessions"] = []
                logger.error(f"Error listing sessions: {sessions_result.get('error')}")
        except Exception as e:
            status_info["active_sessions"] = []
            logger.error(f"Error including sessions in status: {str(e)}")
    
    # Include system metrics if requested
    if include_metrics:
        try:
            metrics = {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage(BASE_DIR).percent
            }
            
            # Get process-specific metrics
            process = psutil.Process()
            process_metrics = {
                "process_cpu_percent": process.cpu_percent(),
                "process_memory_mb": process.memory_info().rss / (1024 * 1024),
                "process_threads": process.num_threads(),
                "process_open_files": len(process.open_files())
            }
            
            metrics.update(process_metrics)
            status_info["metrics"] = metrics
            
            # Update status based on metrics
            if metrics["cpu_percent"] > 90 or metrics["memory_percent"] > 90:
                status_info["status"] = "degraded"
        except Exception as e:
            logger.error(f"Error getting system metrics: {str(e)}")
            status_info["metrics"] = {"error": str(e)}
    
    logger.info(f"System status: {status_info['status']}")
    
    return status_info

def memory_optimize(target_session: Optional[str] = None, level: str = "medium") -> Dict[str, Any]:
    """
    Optimize system memory usage.
    
    Args:
        target_session: Target session to optimize (optional)
        level: Optimization level (light, medium, aggressive)
        
    Returns:
        Dictionary with optimization results
    """
    bytes_saved = 0
    optimization_details = {}
    
    # Validate optimization level
    if level not in ["light", "medium", "aggressive"]:
        logger.error(f"Invalid optimization level: {level}")
        return {
            "success": False,
            "error": f"Invalid optimization level: {level}. Valid levels: light, medium, aggressive"
        }
    
    # Get memory usage before optimization
    process = psutil.Process()
    memory_before = process.memory_info().rss
    
    # Optimize specific session if specified
    if target_session:
        try:
            logger.info(f"Optimizing session: {target_session}")
            
            # Import session tools
            from continuity_protocol.tools.session import session_restore, session_save
            
            # Restore session
            restore_result = session_restore(target_session)
            if not restore_result["success"]:
                logger.error(f"Error restoring session for optimization: {restore_result.get('error')}")
                return {
                    "success": False,
                    "error": f"Error restoring session for optimization: {restore_result.get('error')}"
                }
            
            # Get session content
            content = restore_result["content"]
            
            # Apply optimization based on level
            if level == "light":
                # Light optimization: remove unnecessary whitespace in strings
                bytes_saved += _optimize_strings(content)
            elif level == "medium":
                # Medium optimization: remove unnecessary whitespace and compress repetitive data
                bytes_saved += _optimize_strings(content)
                bytes_saved += _optimize_repetitive_data(content)
            elif level == "aggressive":
                # Aggressive optimization: all of the above plus truncate history
                bytes_saved += _optimize_strings(content)
                bytes_saved += _optimize_repetitive_data(content)
                bytes_saved += _truncate_history(content)
            
            # Save optimized session
            compression_level = {"light": 0, "medium": 1, "aggressive": 2}[level]
            save_result = session_save(target_session, content, compression_level)
            
            if not save_result["success"]:
                logger.error(f"Error saving optimized session: {save_result.get('error')}")
                return {
                    "success": False,
                    "error": f"Error saving optimized session: {save_result.get('error')}"
                }
            
            optimization_details["session"] = {
                "session_id": target_session,
                "bytes_saved": bytes_saved,
                "compression_level": compression_level
            }
        except Exception as e:
            logger.error(f"Error optimizing session {target_session}: {str(e)}")
            return {
                "success": False,
                "error": f"Error optimizing session: {str(e)}"
            }
    else:
        # Perform system-wide optimization
        logger.info(f"Performing system-wide memory optimization (level: {level})")
        
        try:
            # Force garbage collection
            import gc
            gc.collect()
            
            # Clear context cache
            bytes_saved += _clear_context_cache()
            
            # Optimize sessions based on level
            if level in ["medium", "aggressive"]:
                bytes_saved += _optimize_all_sessions(level)
            
            # Remove temporary files
            if level == "aggressive":
                bytes_saved += _clean_temp_files()
            
            optimization_details["system"] = {
                "garbage_collection": True,
                "context_cache_cleared": True,
                "sessions_optimized": level in ["medium", "aggressive"],
                "temp_files_cleaned": level == "aggressive"
            }
        except Exception as e:
            logger.error(f"Error performing system-wide optimization: {str(e)}")
            return {
                "success": False,
                "error": f"Error performing system-wide optimization: {str(e)}"
            }
    
    # Get memory usage after optimization
    memory_after = process.memory_info().rss
    memory_saved = memory_before - memory_after
    
    logger.info(f"Memory optimization completed. Bytes saved: {bytes_saved}, Memory reduced: {memory_saved / (1024 * 1024):.2f} MB")
    
    return {
        "success": True,
        "bytes_saved": bytes_saved,
        "memory_reduced_bytes": memory_saved,
        "memory_reduced_mb": memory_saved / (1024 * 1024),
        "optimization_level": level,
        "optimization_details": optimization_details
    }

# Helper functions for memory optimization

def _optimize_strings(data: Any) -> int:
    """Optimize strings in data structure by removing unnecessary whitespace"""
    bytes_saved = 0
    
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str) and len(value) > 100:
                # For long strings, remove extra whitespace
                original_size = len(value.encode())
                optimized = ' '.join(value.split())
                new_size = len(optimized.encode())
                
                if new_size < original_size:
                    data[key] = optimized
                    bytes_saved += (original_size - new_size)
            elif isinstance(value, (dict, list)):
                bytes_saved += _optimize_strings(value)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, str) and len(item) > 100:
                original_size = len(item.encode())
                optimized = ' '.join(item.split())
                new_size = len(optimized.encode())
                
                if new_size < original_size:
                    data[i] = optimized
                    bytes_saved += (original_size - new_size)
            elif isinstance(item, (dict, list)):
                bytes_saved += _optimize_strings(item)
    
    return bytes_saved

def _optimize_repetitive_data(data: Any) -> int:
    """Optimize repetitive data in structure"""
    # This is a placeholder for a more sophisticated optimization
    # In a real implementation, we would identify and deduplicate repetitive data
    return 0

def _truncate_history(data: Any) -> int:
    """Truncate history in data structure"""
    bytes_saved = 0
    
    # Look for common history fields
    if isinstance(data, dict):
        for key in ["history", "conversation_history", "messages"]:
            if key in data and isinstance(data[key], list):
                original_size = len(json.dumps(data[key]).encode())
                
                # Keep only the last 10 items
                if len(data[key]) > 10:
                    data[key] = data[key][-10:]
                
                new_size = len(json.dumps(data[key]).encode())
                bytes_saved += (original_size - new_size)
    
    return bytes_saved

def _clear_context_cache() -> int:
    """Clear context cache and return bytes saved"""
    bytes_saved = 0
    
    # Clear expired contexts
    contexts_dir = os.path.join(BASE_DIR, "data", "contexts")
    if os.path.exists(contexts_dir):
        for namespace in os.listdir(contexts_dir):
            namespace_dir = os.path.join(contexts_dir, namespace)
            if os.path.isdir(namespace_dir):
                for filename in os.listdir(namespace_dir):
                    if filename.endswith(".json"):
                        file_path = os.path.join(namespace_dir, filename)
                        try:
                            with open(file_path, 'r') as f:
                                context_data = json.load(f)
                            
                            # Check if context has expired
                            if context_data.get("expires_at"):
                                expires_at = datetime.fromisoformat(context_data["expires_at"])
                                if datetime.now() > expires_at:
                                    bytes_saved += os.path.getsize(file_path)
                                    os.remove(file_path)
                        except Exception as e:
                            logger.error(f"Error clearing context cache for {file_path}: {str(e)}")
    
    return bytes_saved

def _optimize_all_sessions(level: str) -> int:
    """Optimize all sessions and return bytes saved"""
    bytes_saved = 0
    
    # Find all sessions
    sessions_dir = os.path.join(BASE_DIR, "data", "sessions")
    if os.path.exists(sessions_dir):
        for session_id in os.listdir(sessions_dir):
            session_dir = os.path.join(sessions_dir, session_id)
            if os.path.isdir(session_dir):
                # Call memory_optimize for each session
                try:
                    result = memory_optimize(session_id, level)
                    if result["success"]:
                        bytes_saved += result["bytes_saved"]
                except Exception as e:
                    logger.error(f"Error optimizing session {session_id}: {str(e)}")
    
    return bytes_saved

def _clean_temp_files() -> int:
    """Clean temporary files and return bytes saved"""
    bytes_saved = 0
    
    # Define temp directories to clean
    temp_dirs = [
        os.path.join(BASE_DIR, "data", "temp"),
        os.path.join(BASE_DIR, "logs", "temp")
    ]
    
    for temp_dir in temp_dirs:
        if os.path.exists(temp_dir):
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        bytes_saved += os.path.getsize(file_path)
                        os.remove(file_path)
                except Exception as e:
                    logger.error(f"Error cleaning temp file {file_path}: {str(e)}")
    
    return bytes_saved