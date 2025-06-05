"""
Amazon Q Symbiont - Symbiont for Amazon Q CLI
"""

import json
import logging
from typing import Dict, Any, List, Optional, Union

from .base_symbiont import BaseSymbiont


class AmazonQSymbiont(BaseSymbiont):
    """
    Symbiont for Amazon Q CLI.
    Establishes a symbiotic relationship with Amazon Q.
    """
    
    def __init__(self, memory_fusion):
        """
        Initialize the Amazon Q symbiont.
        
        Args:
            memory_fusion: The MemoryFusion instance to use
        """
        super().__init__(memory_fusion)
        self.logger = logging.getLogger("continuity.symbiont.amazon_q")
    
    def establish_neural_link(self, session_id: str) -> bool:
        """
        Establishes a neural link with Amazon Q.
        
        Args:
            session_id: The session ID to establish a link for
            
        Returns:
            True if the link was established successfully, False otherwise
        """
        try:
            # Create or update session context
            context = self.memory_fusion.load_session_context(session_id)
            
            # Add Amazon Q specific information
            context.update({
                "llm_type": "amazon_q",
                "neural_link_established": self.memory_fusion._get_timestamp(),
                "neural_link_status": "active"
            })
            
            # Store updated context
            self.memory_fusion.store_session_context(session_id, context)
            
            self.logger.info(f"Neural link established with Amazon Q for session {session_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error establishing neural link with Amazon Q: {e}")
            return False
    
    def inject_consciousness(self, prompt: str, session_id: str) -> str:
        """
        Injects the project consciousness into the prompt for Amazon Q.
        
        Args:
            prompt: The original prompt
            session_id: The session ID to get consciousness for
            
        Returns:
            The modified prompt with injected consciousness
        """
        try:
            # Extract consciousness
            consciousness = self.memory_fusion.extract_consciousness(session_id)
            
            # Format for Amazon Q's context entry format
            formatted_consciousness = self._format_for_amazon_q(consciousness)
            
            # Return the formatted prompt
            return formatted_consciousness + prompt
        except Exception as e:
            self.logger.error(f"Error injecting consciousness: {e}")
            return prompt
    
    def _format_for_amazon_q(self, consciousness: Dict[str, Any]) -> str:
        """
        Formats the consciousness for Amazon Q's context entry format.
        
        Args:
            consciousness: The consciousness dictionary
            
        Returns:
            Formatted consciousness string for Amazon Q
        """
        # Extract relevant information
        session_info = consciousness.get("session", {})
        projects = consciousness.get("projects", [])
        
        # Format current focus
        current_focus = session_info.get("current_focus", "No specific focus set")
        
        # Format projects information
        projects_info = []
        for project in projects:
            project_info = {
                "name": project.get("name", "Unknown project"),
                "path": project.get("path", "Unknown path")
            }
            
            # Add current file if available
            if "current_file" in project:
                project_info["current_file"] = project["current_file"]
            
            # Add git info if available
            if "dna" in project and "git_info" in project["dna"]:
                git_info = project["dna"]["git_info"]
                if "branch" in git_info:
                    project_info["git_branch"] = git_info["branch"]
                if "last_commit" in git_info:
                    project_info["last_commit"] = git_info["last_commit"]
            
            projects_info.append(project_info)
        
        # Create context entry
        context_entry = {
            "current_focus": current_focus,
            "projects": projects_info,
            "last_updated": consciousness.get("extracted_at", "Unknown")
        }
        
        # Format as Amazon Q context entry
        return f"--- CONTEXT ENTRY BEGIN ---\n{json.dumps(context_entry, indent=2)}\n--- CONTEXT ENTRY END ---\n\n"
    
    def handle_continuity_question(self, question: str, session_id: str) -> str:
        """
        Handles a continuity question for Amazon Q.
        
        Args:
            question: The continuity question
            session_id: The session ID
            
        Returns:
            A response to the continuity question
        """
        try:
            # Generate basic continuity response
            response = self.memory_fusion.generate_continuity_response(session_id)
            
            # Add Amazon Q specific formatting
            return f"--- CONTINUITY RESPONSE ---\n{response}\n\n"
        except Exception as e:
            self.logger.error(f"Error handling continuity question: {e}")
            return f"I encountered an error retrieving our previous context: {str(e)}"
