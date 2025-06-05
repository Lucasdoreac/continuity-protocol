"""
Base Symbiont - Base class for all LLM symbionts
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union


class BaseSymbiont(ABC):
    """
    Base class for all LLM symbionts.
    Establishes a symbiotic relationship with different language models.
    """
    
    def __init__(self, memory_fusion):
        """
        Initialize the symbiont.
        
        Args:
            memory_fusion: The MemoryFusion instance to use for storing and retrieving context
        """
        self.memory_fusion = memory_fusion
        self.logger = logging.getLogger(f"continuity.symbiont.{self.__class__.__name__}")
    
    @abstractmethod
    def establish_neural_link(self, session_id: str) -> bool:
        """
        Establishes a neural link with the model.
        
        Args:
            session_id: The session ID to establish a link for
            
        Returns:
            True if the link was established successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def inject_consciousness(self, prompt: str, session_id: str) -> str:
        """
        Injects the project consciousness into the prompt.
        
        Args:
            prompt: The original prompt
            session_id: The session ID to get consciousness for
            
        Returns:
            The modified prompt with injected consciousness
        """
        pass
    
    def _fuse_consciousness_with_prompt(self, consciousness: Dict[str, Any], prompt: str) -> str:
        """
        Fuses the project consciousness with the user prompt.
        
        Args:
            consciousness: The project consciousness dictionary
            prompt: The original prompt
            
        Returns:
            The fused prompt
        """
        # Default implementation - override in subclasses for model-specific formatting
        consciousness_str = self._format_consciousness(consciousness)
        return f"{consciousness_str}\n\n{prompt}"
    
    def _format_consciousness(self, consciousness: Dict[str, Any]) -> str:
        """
        Formats the consciousness dictionary as a string.
        
        Args:
            consciousness: The consciousness dictionary
            
        Returns:
            Formatted consciousness string
        """
        parts = ["# Project Consciousness"]
        
        # Session info
        if "session" in consciousness:
            session = consciousness["session"]
            if "current_focus" in session:
                parts.append(f"## Current Focus\n{session['current_focus']}")
        
        # Projects
        if "projects" in consciousness and consciousness["projects"]:
            parts.append("## Active Projects")
            for project in consciousness["projects"]:
                parts.append(f"- **{project.get('name', 'Project')}**: {project.get('path', 'Path not available')}")
                if "current_file" in project:
                    parts.append(f"  - Current file: `{project['current_file']}`")
                if "dna" in project and "git_info" in project["dna"] and "branch" in project["dna"]["git_info"]:
                    parts.append(f"  - Branch: `{project['dna']['git_info']['branch']}`")
        
        # Join all parts
        return "\n\n".join(parts)
    
    def handle_continuity_question(self, question: str, session_id: str) -> str:
        """
        Handles a continuity question like "where did we leave off?".
        
        Args:
            question: The continuity question
            session_id: The session ID
            
        Returns:
            A response to the continuity question
        """
        try:
            # Generate continuity response
            return self.memory_fusion.generate_continuity_response(session_id)
        except Exception as e:
            self.logger.error(f"Error handling continuity question: {e}")
            return f"I encountered an error retrieving our previous context: {str(e)}"
    
    def process_input(self, user_input: str, session_id: str) -> Union[str, Dict[str, Any]]:
        """
        Processes user input, handling continuity questions and injecting consciousness.
        
        Args:
            user_input: The user input
            session_id: The session ID
            
        Returns:
            Either a direct response (for continuity questions) or the modified input with injected consciousness
        """
        # Check if this is a continuity question
        if self.memory_fusion.detect_continuity_question(user_input):
            return self.handle_continuity_question(user_input, session_id)
        
        # Otherwise, inject consciousness
        return self.inject_consciousness(user_input, session_id)
    
    def update_session_context(self, session_id: str, context_update: Dict[str, Any]) -> None:
        """
        Updates the session context.
        
        Args:
            session_id: The session ID
            context_update: Dictionary containing context updates
        """
        # Load existing context
        existing_context = self.memory_fusion.load_session_context(session_id)
        
        # Update context
        for key, value in context_update.items():
            if key in existing_context and isinstance(existing_context[key], dict) and isinstance(value, dict):
                existing_context[key].update(value)
            else:
                existing_context[key] = value
        
        # Store updated context
        self.memory_fusion.store_session_context(session_id, existing_context)
    
    def add_to_history(self, session_id: str, entry_type: str, content: str) -> None:
        """
        Adds an entry to the session history.
        
        Args:
            session_id: The session ID
            entry_type: The type of entry (e.g., "user", "assistant", "system")
            content: The content of the entry
        """
        # Load existing context
        existing_context = self.memory_fusion.load_session_context(session_id)
        
        # Ensure history exists
        if "history" not in existing_context:
            existing_context["history"] = []
        
        # Add entry
        existing_context["history"].append({
            "type": entry_type,
            "content": content,
            "timestamp": self.memory_fusion._get_timestamp()
        })
        
        # Trim history if too long
        if len(existing_context["history"]) > 100:
            existing_context["history"] = existing_context["history"][-100:]
        
        # Store updated context
        self.memory_fusion.store_session_context(session_id, existing_context)
