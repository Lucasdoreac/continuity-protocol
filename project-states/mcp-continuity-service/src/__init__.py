"""
MCP Continuity Service - Main Package
"""

from .core import ContinuityManager, SessionManager, ContextDetector, RecoveryEngine

__version__ = "1.0.0"
__title__ = "MCP Continuity Service"
__description__ = "Professional continuity service for LLMs with MCP integration"
__author__ = "MCP Continuity Team"
__license__ = "MIT"

__all__ = [
    "ContinuityManager",
    "SessionManager",
    "ContextDetector", 
    "RecoveryEngine"
]
