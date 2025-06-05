"""
MCP Continuity Service - Core Continuity Manager
Manages the main continuity workflow and orchestrates all components.
"""

from typing import Dict, List, Optional, Any
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

from .session_manager import SessionManager
from .context_detector import ContextDetector
from .recovery_engine import RecoveryEngine
from ..utils.smart_cleanup import SmartCleanup
from ..utils.emergency_system import EmergencySystem
from ..services.llm_service import LLMService
from ..services.applescript_service import AppleScriptService
from ..services.bash_scripts_service import BashScriptsService


class ContinuityManager:
    """
    Main continuity manager that orchestrates the entire continuity workflow.
    
    This class is responsible for:
    - Processing user inputs and determining appropriate actions
    - Handling continuity questions automatically
    - Coordinating recovery operations
    - Managing session state and context
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize core components
        self.session_manager = SessionManager(self.config)
        self.context_detector = ContextDetector(self.config)
        self.recovery_engine = RecoveryEngine(self.config)
        self.smart_cleanup = SmartCleanup(self.config)
        self.emergency_system = EmergencySystem(self.config)
        self.bash_scripts = BashScriptsService(self.config)
        
        # State management
        self.active_sessions: Dict[str, Dict] = {}
        self.project_states: Dict[str, Dict] = {}
        
    async def process_user_input(self, user_input: str, session_id: str) -> Dict[str, Any]:
        """
        Main entry point for processing user input.
        
        Args:
            user_input: The user's input text
            session_id: Unique session identifier
            
        Returns:
            Dictionary with response data and metadata
        """
        try:
            self.logger.info(f"Processing input for session {session_id}: {user_input[:50]}...")
            
            # Create emergency backup before processing
            await self.emergency_system.create_emergency_backup(session_id)
            
            # Detect if this is a continuity question
            if await self.context_detector.is_continuity_question(user_input):
                return await self.handle_continuity_request(session_id)
            
            # For substantive input, preserve it first
            await self.preserve_input(user_input, session_id)
            
            # Check if recovery is needed
            if await self.context_detector.needs_recovery(session_id):
                await self.recovery_engine.auto_recover(session_id)
            
            # Continue with normal session processing
            return await self.continue_session(user_input, session_id)
            
        except Exception as e:
            self.logger.error(f"Error processing input: {e}")
            return {
                "type": "error",
                "message": f"Error processing input: {str(e)}",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
    
    async def handle_continuity_request(self, session_id: str) -> Dict[str, Any]:
        """
        Handle continuity questions like 'onde paramos?'
        Uses bash scripts as primary method with professional fallback
        
        Args:
            session_id: Session identifier
            
        Returns:
            Complete context response
        """
        self.logger.info(f"Handling continuity request for session {session_id}")
        
        try:
            # Try bash scripts first (proven to work)
            bash_result = await self.bash_scripts.recovery_where_stopped()
            
            if bash_result["success"]:
                return {
                    "type": "continuity_response", 
                    "content": bash_result["output"],
                    "method": "bash_scripts",
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Fallback to professional method if bash fails
            self.logger.warning("Bash scripts failed, using professional fallback")
            
            # Load full context
            context = await self.recovery_engine.load_full_context(session_id)
            
            # Get active projects
            active_projects = await self.get_active_projects(session_id)
            
            # Get critical missions
            critical_missions = await self.get_critical_missions(session_id)
            
            # Get next recommended actions
            next_actions = await self.get_next_actions(session_id, context)
            
            return {
                "type": "continuity_response",
                "context": context,
                "projects": active_projects,
                "critical_missions": critical_missions,
                "next_actions": next_actions,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "summary": self.generate_context_summary(context, active_projects, critical_missions)
            }
            
        except Exception as e:
            self.logger.error(f"Error handling continuity request: {e}")
            return {
                "type": "error",
                "message": f"Error loading context: {str(e)}",
                "session_id": session_id
            }

    async def preserve_input(self, user_input: str, session_id: str):
        """Preserve user input for potential recovery"""
        await self.session_manager.save_input(user_input, session_id)
    
    async def continue_session(self, user_input: str, session_id: str) -> Dict[str, Any]:
        """Continue normal session processing"""
        return {
            "type": "session_continue",
            "message": "Session continuing normally",
            "user_input": user_input,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_active_projects(self, session_id: str) -> List[Dict]:
        """Get list of active projects for session"""
        return await self.session_manager.get_active_projects(session_id)
    
    async def get_critical_missions(self, session_id: str) -> List[Dict]:
        """Get critical missions that need attention"""
        return await self.recovery_engine.get_critical_missions(session_id)
    
    async def get_next_actions(self, session_id: str, context: Dict) -> List[str]:
        """Generate recommended next actions based on context"""
        actions = []
        
        if context.get("needs_recovery"):
            actions.append("Execute automatic recovery")
        
        if context.get("orphaned_files"):
            actions.append("Process orphaned files")
        
        if context.get("active_projects"):
            actions.append("Continue with active projects")
        
        return actions
    
    def generate_context_summary(self, context: Dict, projects: List, missions: List) -> str:
        """Generate human-readable context summary"""
        summary_parts = []
        
        if projects:
            summary_parts.append(f"{len(projects)} active project(s)")
        
        if missions:
            summary_parts.append(f"{len(missions)} critical mission(s)")
        
        if context.get("needs_recovery"):
            summary_parts.append("recovery needed")
        
        return "Status: " + ", ".join(summary_parts) if summary_parts else "No active context"
    
    async def cleanup_session(self, session_id: str):
        """Clean up session resources"""
        await self.smart_cleanup.cleanup_session(session_id)
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
    
    async def emergency_freeze(self, session_id: str) -> str:
        """Create emergency freeze of current state"""
        return await self.emergency_system.freeze(session_id)
    
    async def emergency_unfreeze(self, freeze_id: str) -> bool:
        """Restore from emergency freeze"""
        return await self.emergency_system.unfreeze(freeze_id)
    # Add imports for new services
    from ..services.llm_service import LLMService
    from ..services.applescript_service import AppleScriptService
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize core components
        self.session_manager = SessionManager(self.config)
        self.context_detector = ContextDetector(self.config)
        self.recovery_engine = RecoveryEngine(self.config)
        self.smart_cleanup = SmartCleanup(self.config)
        self.emergency_system = EmergencySystem(self.config)
        
        # Initialize new services
        self.llm_service = LLMService(self.config.get('llm', {}))
        self.applescript_service = AppleScriptService(self.config.get('applescript', {}))
        
        # State management
        self.active_sessions: Dict[str, Dict] = {}
        self.project_states: Dict[str, Dict] = {}
    
    async def handle_continuity_request(self, session_id: str) -> Dict[str, Any]:
        """
        Enhanced continuity handler with AppleScript and LLM integration
        """
        self.logger.info(f"Handling continuity request for session {session_id}")
        
        try:
            # Load session context
            context = await self.recovery_engine.load_full_context(session_id)
            
            # Capture current system context via AppleScript
            if self.applescript_service.available:
                system_context = await self.applescript_service.capture_system_context()
                context['system_context'] = system_context
            
            # Get active projects and missions
            active_projects = await self.get_active_projects(session_id)
            critical_missions = await self.get_critical_missions(session_id)
            
            # Generate intelligent response using LLM
            messages = [
                {
                    "role": "system",
                    "content": self._get_continuity_system_prompt()
                },
                {
                    "role": "user", 
                    "content": "onde paramos?"
                }
            ]
            
            # Stream response from LLM
            llm_response_chunks = []
            async for chunk in self.llm_service.chat_with_continuity(
                messages=messages,
                session_id=session_id,
                continuity_context=context
            ):
                llm_response_chunks.append(chunk)
            
            llm_response = "".join(llm_response_chunks)
            
            # Save context to Apple Notes if enabled
            if self.applescript_service.available and self.config.get('applescript', {}).get('save_to_notes'):
                await self.applescript_service.save_continuity_note(session_id, context)
            
            return {
                "type": "continuity_response",
                "content": llm_response,
                "context": context,
                "projects": active_projects,
                "critical_missions": critical_missions,
                "system_context": context.get('system_context', {}),
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "summary": self.generate_context_summary(context, active_projects, critical_missions)
            }
            
        except Exception as e:
            self.logger.error(f"Error handling continuity request: {e}")
            return {
                "type": "error",
                "message": f"Error loading context: {str(e)}",
                "session_id": session_id
            }
    
    def _get_continuity_system_prompt(self) -> str:
        """Get system prompt for continuity responses"""
        return """
Você é um assistente especializado em continuidade de contexto para desenvolvedores e profissionais.

Quando o usuário disser "onde paramos?" ou perguntas similares, você deve:

1. Analisar o contexto completo fornecido (projetos ativos, missões críticas, contexto do sistema)
2. Apresentar um resumo claro e organizado do que estava sendo trabalhado
3. Destacar próximas ações e prioridades
4. Mencionar recursos relevantes (arquivos abertos, aplicações ativas)
5. Sugerir como continuar o trabalho

Responda de forma natural, clara e útil. Use emojis para organizar visualmente a informação.
"""
    
    async def get_llm_providers(self) -> List[str]:
        """Get available LLM providers"""
        return self.llm_service.get_available_providers()
    
    async def health_check_llm(self) -> Dict[str, Any]:
        """Check health of LLM providers"""
        return await self.llm_service.health_check()
