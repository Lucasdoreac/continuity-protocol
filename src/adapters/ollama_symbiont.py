"""
Ollama Symbiont - Symbiont for Ollama LLM
"""

import json
import logging
from typing import Dict, Any, List, Optional, Union

try:
    from .base_symbiont import BaseSymbiont
except ImportError:
    from continuity.adapters.base_symbiont import BaseSymbiont


class OllamaSymbiont(BaseSymbiont):
    """
    Symbiont for Ollama LLM.
    Establishes a symbiotic relationship with Ollama.
    """
    
    def __init__(self, memory_fusion):
        """
        Initialize the Ollama symbiont.
        
        Args:
            memory_fusion: The MemoryFusion instance to use
        """
        super().__init__(memory_fusion)
        self.logger = logging.getLogger("continuity.symbiont.ollama")
        self.ollama_url = "http://localhost:11434/api"
    
    def establish_neural_link(self, session_id: str) -> bool:
        """
        Establishes a neural link with Ollama.
        
        Args:
            session_id: The session ID to establish a link for
            
        Returns:
            True if the link was established successfully, False otherwise
        """
        try:
            # Create or update session context
            context = self.memory_fusion.load_session_context(session_id)
            
            # Add Ollama specific information
            context.update({
                "llm_type": "ollama",
                "neural_link_established": self.memory_fusion._get_timestamp(),
                "neural_link_status": "active",
                "ollama_url": self.ollama_url
            })
            
            # Store updated context
            self.memory_fusion.store_session_context(session_id, context)
            
            self.logger.info(f"Neural link established with Ollama for session {session_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error establishing neural link with Ollama: {e}")
            return False
    
    def inject_consciousness(self, prompt: str, session_id: str) -> str:
        """
        Injects the project consciousness into the prompt for Ollama.
        
        Args:
            prompt: The original prompt
            session_id: The session ID to get consciousness for
            
        Returns:
            The modified prompt with injected consciousness
        """
        try:
            # Extract consciousness
            consciousness = self.memory_fusion.extract_consciousness(session_id)
            
            # Format for Ollama's system message format
            formatted_consciousness = self._format_for_ollama(consciousness)
            
            # Return the formatted prompt
            return formatted_consciousness + prompt
        except Exception as e:
            self.logger.error(f"Error injecting consciousness: {e}")
            return prompt
    
    def _format_for_ollama(self, consciousness: Dict[str, Any]) -> str:
        """
        Formats the consciousness for Ollama's format.
        
        Args:
            consciousness: The consciousness dictionary
            
        Returns:
            Formatted consciousness string for Ollama
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
        
        # Create system message
        system_message = f"""You are a development assistant with access to the following project context:

Current Focus: {current_focus}

Active Projects:
{json.dumps(projects_info, indent=2)}

Last Updated: {consciousness.get("extracted_at", "Unknown")}

Use this context to provide relevant assistance. When asked "where did we leave off?" or similar questions, summarize the current state of work.

"""
        
        return system_message
    
    def handle_continuity_question(self, question: str, session_id: str) -> str:
        """
        Handles a continuity question for Ollama.
        
        Args:
            question: The continuity question
            session_id: The session ID
            
        Returns:
            A response to the continuity question
        """
        try:
            # Generate basic continuity response
            response = self.memory_fusion.generate_continuity_response(session_id)
            
            # Add Ollama specific formatting
            return response
        except Exception as e:
            self.logger.error(f"Error handling continuity question: {e}")
            return f"I encountered an error retrieving our previous context: {str(e)}"
    
    async def generate_response(self, prompt: str, session_id: str, model: str = "llama3") -> str:
        """
        Generates a response from Ollama.
        
        Args:
            prompt: The prompt to send to Ollama
            session_id: The session ID
            model: The Ollama model to use
            
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
            
            # Otherwise, send to Ollama
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.ollama_url}/generate",
                    json={
                        "model": model,
                        "prompt": processed_prompt,
                        "stream": False
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("response", "")
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Error from Ollama API: {error_text}")
                        return f"Error generating response: {response.status}"
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return f"Error generating response: {str(e)}"
