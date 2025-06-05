"""
LLM Studio Symbiont - Symbiont for LLM Studio
"""

import json
import logging
from typing import Dict, Any, List, Optional, Union

try:
    from .base_symbiont import BaseSymbiont
except ImportError:
    from continuity.adapters.base_symbiont import BaseSymbiont


class LLMStudioSymbiont(BaseSymbiont):
    """
    Symbiont for LLM Studio.
    Establishes a symbiotic relationship with LLM Studio.
    """
    
    def __init__(self, memory_fusion, api_url: str = "http://localhost:8000"):
        """
        Initialize the LLM Studio symbiont.
        
        Args:
            memory_fusion: The MemoryFusion instance to use
            api_url: URL for the LLM Studio API
        """
        super().__init__(memory_fusion)
        self.logger = logging.getLogger("continuity.symbiont.llm_studio")
        self.api_url = api_url
    
    def establish_neural_link(self, session_id: str) -> bool:
        """
        Establishes a neural link with LLM Studio.
        
        Args:
            session_id: The session ID to establish a link for
            
        Returns:
            True if the link was established successfully, False otherwise
        """
        try:
            # Create or update session context
            context = self.memory_fusion.load_session_context(session_id)
            
            # Add LLM Studio specific information
            context.update({
                "llm_type": "llm_studio",
                "neural_link_established": self.memory_fusion._get_timestamp(),
                "neural_link_status": "active",
                "llm_studio_url": self.api_url
            })
            
            # Store updated context
            self.memory_fusion.store_session_context(session_id, context)
            
            self.logger.info(f"Neural link established with LLM Studio for session {session_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error establishing neural link with LLM Studio: {e}")
            return False
    
    def inject_consciousness(self, prompt: str, session_id: str) -> str:
        """
        Injects the project consciousness into the prompt for LLM Studio.
        
        Args:
            prompt: The original prompt
            session_id: The session ID to get consciousness for
            
        Returns:
            The modified prompt with injected consciousness
        """
        try:
            # Extract consciousness
            consciousness = self.memory_fusion.extract_consciousness(session_id)
            
            # Format for LLM Studio's format
            formatted_consciousness = self._format_for_llm_studio(consciousness)
            
            # Return the formatted prompt
            return formatted_consciousness + prompt
        except Exception as e:
            self.logger.error(f"Error injecting consciousness: {e}")
            return prompt
    
    def _format_for_llm_studio(self, consciousness: Dict[str, Any]) -> str:
        """
        Formats the consciousness for LLM Studio's format.
        
        Args:
            consciousness: The consciousness dictionary
            
        Returns:
            Formatted consciousness string for LLM Studio
        """
        # Extract relevant information
        session_info = consciousness.get("session", {})
        projects = consciousness.get("projects", [])
        
        # Format current focus
        current_focus = session_info.get("current_focus", "No specific focus set")
        
        # Format projects information
        projects_text = ""
        for i, project in enumerate(projects):
            project_name = project.get("name", "Unknown project")
            project_path = project.get("path", "Unknown path")
            
            projects_text += f"Project {i+1}: {project_name} ({project_path})\n"
            
            # Add current file if available
            if "current_file" in project:
                projects_text += f"Current file: {project['current_file']}\n"
            
            # Add git info if available
            if "dna" in project and "git_info" in project["dna"]:
                git_info = project["dna"]["git_info"]
                if "branch" in git_info:
                    projects_text += f"Git branch: {git_info['branch']}\n"
                if "last_commit" in git_info:
                    projects_text += f"Last commit: {git_info['last_commit']}\n"
            
            projects_text += "\n"
        
        # Create context header
        context_header = f"""[CONTEXT]
Current Focus: {current_focus}

Active Projects:
{projects_text}
Last Updated: {consciousness.get("extracted_at", "Unknown")}
[/CONTEXT]

"""
        
        return context_header
    
    def handle_continuity_question(self, question: str, session_id: str) -> str:
        """
        Handles a continuity question for LLM Studio.
        
        Args:
            question: The continuity question
            session_id: The session ID
            
        Returns:
            A response to the continuity question
        """
        try:
            # Generate basic continuity response
            response = self.memory_fusion.generate_continuity_response(session_id)
            
            # Add LLM Studio specific formatting
            return response
        except Exception as e:
            self.logger.error(f"Error handling continuity question: {e}")
            return f"I encountered an error retrieving our previous context: {str(e)}"
    
    async def generate_response(self, prompt: str, session_id: str, model_id: Optional[str] = None) -> str:
        """
        Generates a response from LLM Studio.
        
        Args:
            prompt: The prompt to send to LLM Studio
            session_id: The session ID
            model_id: Optional model ID to use
            
        Returns:
            The generated response
        """
        try:
            import aiohttp
            
            # Process the prompt
            processed_prompt = self.process_input(prompt, session_id)
            
            # If it's a continuity question, return the response directly
            if isinstance(processed_prompt, str) and processed_prompt.startswith("# Continuidade da Sessão"):
                return processed_prompt
            
            # Otherwise, send to LLM Studio
            async with aiohttp.ClientSession() as session:
                payload = {
                    "prompt": processed_prompt,
                    "max_tokens": 1024,
                    "temperature": 0.7
                }
                
                if model_id:
                    payload["model_id"] = model_id
                
                async with session.post(
                    f"{self.api_url}/generate",
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("text", "")
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Error from LLM Studio API: {error_text}")
                        return f"Error generating response: {response.status}"
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return f"Error generating response: {str(e)}"
