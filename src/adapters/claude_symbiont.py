"""
Claude Symbiont - Symbiont for Claude Desktop
"""

import json
import logging
from typing import Dict, Any, List, Optional, Union

from .base_symbiont import BaseSymbiont


class ClaudeSymbiont(BaseSymbiont):
    """
    Symbiont for Claude Desktop.
    Establishes a symbiotic relationship with Claude.
    """
    
    def __init__(self, memory_fusion):
        """
        Initialize the Claude symbiont.
        
        Args:
            memory_fusion: The MemoryFusion instance to use
        """
        super().__init__(memory_fusion)
        self.logger = logging.getLogger("continuity.symbiont.claude")
    
    def establish_neural_link(self, session_id: str) -> bool:
        """
        Establishes a neural link with Claude.
        
        Args:
            session_id: The session ID to establish a link for
            
        Returns:
            True if the link was established successfully, False otherwise
        """
        try:
            # Create or update session context
            context = self.memory_fusion.load_session_context(session_id)
            
            # Add Claude specific information
            context.update({
                "llm_type": "claude",
                "neural_link_established": self.memory_fusion._get_timestamp(),
                "neural_link_status": "active"
            })
            
            # Store updated context
            self.memory_fusion.store_session_context(session_id, context)
            
            self.logger.info(f"Neural link established with Claude for session {session_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error establishing neural link with Claude: {e}")
            return False
    
    def inject_consciousness(self, prompt: str, session_id: str) -> str:
        """
        Injects the project consciousness into the prompt for Claude.
        
        Args:
            prompt: The original prompt
            session_id: The session ID to get consciousness for
            
        Returns:
            The modified prompt with injected consciousness
        """
        try:
            # Extract consciousness
            consciousness = self.memory_fusion.extract_consciousness(session_id)
            
            # Format for Claude's XML-based context format
            formatted_consciousness = self._format_for_claude(consciousness)
            
            # Return the formatted prompt
            return formatted_consciousness + prompt
        except Exception as e:
            self.logger.error(f"Error injecting consciousness: {e}")
            return prompt
    
    def _format_for_claude(self, consciousness: Dict[str, Any]) -> str:
        """
        Formats the consciousness for Claude's XML-based context format.
        
        Args:
            consciousness: The consciousness dictionary
            
        Returns:
            Formatted consciousness string for Claude
        """
        # Extract relevant information
        session_info = consciousness.get("session", {})
        projects = consciousness.get("projects", [])
        
        # Format current focus
        current_focus = session_info.get("current_focus", "No specific focus set")
        
        # Format projects information
        projects_xml = ""
        for project in projects:
            project_name = project.get("name", "Unknown project")
            project_path = project.get("path", "Unknown path")
            
            project_xml = f"<project>\n  <name>{project_name}</name>\n  <path>{project_path}</path>\n"
            
            # Add current file if available
            if "current_file" in project:
                project_xml += f"  <current_file>{project['current_file']}</current_file>\n"
            
            # Add git info if available
            if "dna" in project and "git_info" in project["dna"]:
                git_info = project["dna"]["git_info"]
                if "branch" in git_info:
                    project_xml += f"  <git_branch>{git_info['branch']}</git_branch>\n"
                if "last_commit" in git_info:
                    project_xml += f"  <last_commit>{git_info['last_commit']}</last_commit>\n"
            
            project_xml += "</project>\n"
            projects_xml += project_xml
        
        # Create XML context
        xml_context = f"""<context>
  <current_focus>{current_focus}</current_focus>
  <projects>
{projects_xml}  </projects>
  <last_updated>{consciousness.get("extracted_at", "Unknown")}</last_updated>
</context>

"""
        
        return xml_context
    
    def handle_continuity_question(self, question: str, session_id: str) -> str:
        """
        Handles a continuity question for Claude.
        
        Args:
            question: The continuity question
            session_id: The session ID
            
        Returns:
            A response to the continuity question
        """
        try:
            # Generate basic continuity response
            response = self.memory_fusion.generate_continuity_response(session_id)
            
            # Add Claude specific formatting
            return f"<continuity_response>\n{response}\n</continuity_response>\n\n"
        except Exception as e:
            self.logger.error(f"Error handling continuity question: {e}")
            return f"I encountered an error retrieving our previous context: {str(e)}"
