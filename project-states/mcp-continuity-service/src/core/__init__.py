"""
MCP Continuity Service - Core Package
"""

from .continuity_manager import ContinuityManager
from .session_manager import SessionManager
from .context_detector import ContextDetector
from .recovery_engine import RecoveryEngine

__version__ = "1.0.0"
__author__ = "MCP Continuity Team"

__all__ = [
    "ContinuityManager",
    "SessionManager", 
    "ContextDetector",
    "RecoveryEngine"
]
