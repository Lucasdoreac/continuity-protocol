"""
Ollama Adapter - Adapter for Ollama LLM
"""

import requests
import json
import logging
from typing import Dict, Any, Optional, List, Union

class OllamaAdapter:
    """Adapter for Ollama LLM."""
    
    def __init__(self, base_url: str = "http://localhost:11434", continuity_url: str = "http://localhost:8765"):
        """
        Initialize the Ollama adapter.
        
        Args:
            base_url: Base URL for Ollama API
            continuity_url: URL for Continuity Protocol server
        """
        self.base_url = base_url
        self.continuity_url = continuity_url
        self.logger = logging.getLogger("continuity.adapters.ollama")
    
    def process_input(self, input_text: str, session_id: str, model: str = "llama3") -> Dict[str, Any]:
        """
        Process input through Continuity Protocol and Ollama.
        
        Args:
            input_text: User input text
            session_id: Session ID
            model: Ollama model to use
            
        Returns:
            Dictionary with response
        """
        # Check if it's a continuity question
        continuity_check = self._check_continuity(input_text, session_id)
        if continuity_check.get("is_continuity_question", False):
            return self._get_continuity_response(session_id)
        
        # Otherwise, inject context and send to Ollama
        context = self._get_context(session_id)
        prompt_with_context = self._format_context(context, input_text)
        
        # Add input to history
        self._update_history(session_id, "user", input_text)
        
        # Generate response
        response_data = self._generate_response(prompt_with_context, model)
        
        # Add response to history
        if "response" in response_data:
            self._update_history(session_id, "assistant", response_data["response"])
        
        return response_data
    
    def _check_continuity(self, input_text: str, session_id: str) -> Dict[str, Any]:
        """
        Check if input is a continuity question.
        
        Args:
            input_text: User input text
            session_id: Session ID
            
        Returns:
            Dictionary with check result
        """
        try:
            response = requests.post(
                f"{self.continuity_url}/continuity/check",
                json={"text": input_text, "session_id": session_id}
            )
            return response.json()
        except Exception as e:
            self.logger.error(f"Error checking continuity: {e}")
            return {"is_continuity_question": False}
    
    def _get_continuity_response(self, session_id: str) -> Dict[str, Any]:
        """
        Get continuity response.
        
        Args:
            session_id: Session ID
            
        Returns:
            Dictionary with continuity response
        """
        try:
            response = requests.post(
                f"{self.continuity_url}/continuity/response",
                json={"session_id": session_id}
            )
            data = response.json()
            return {
                "response": data["response"],
                "type": "continuity_response"
            }
        except Exception as e:
            self.logger.error(f"Error getting continuity response: {e}")
            return {
                "response": f"Error retrieving context: {e}",
                "type": "error"
            }
    
    def _get_context(self, session_id: str) -> Dict[str, Any]:
        """
        Get context for session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Dictionary with context
        """
        try:
            response = requests.post(
                f"{self.continuity_url}/consciousness",
                json={"session_id": session_id}
            )
            return response.json()
        except Exception as e:
            self.logger.error(f"Error getting context: {e}")
            return {}
    
    def _format_context(self, context: Dict[str, Any], input_text: str) -> str:
        """
        Format context for Ollama.
        
        Args:
            context: Context dictionary
            input_text: User input text
            
        Returns:
            Formatted prompt with context
        """
        if not context:
            return input_text
        
        # Extract relevant information
        session = context.get("session", {})
        projects = context.get("projects", [])
        
        # Format context
        context_str = "Context:\n"
        
        if "current_focus" in session:
            context_str += f"Current focus: {session['current_focus']}\n\n"
        
        if projects:
            context_str += "Active projects:\n"
            for project in projects:
                context_str += f"- {project.get('name', 'Unknown project')}\n"
                if "current_file" in project:
                    context_str += f"  Current file: {project['current_file']}\n"
                if "dna" in project and "git_info" in project["dna"] and "branch" in project["dna"]["git_info"]:
                    context_str += f"  Branch: {project['dna']['git_info']['branch']}\n"
            context_str += "\n"
        
        # Add history if available
        if "history" in session:
            history = session["history"]
            if history:
                context_str += "Recent conversation:\n"
                # Get last 5 entries
                for entry in history[-5:]:
                    if "type" in entry and "content" in entry:
                        role = entry["type"].capitalize()
                        content = entry["content"]
                        context_str += f"{role}: {content}\n"
                context_str += "\n"
        
        return f"{context_str}\nUser: {input_text}"
    
    async def generate_response(self, prompt: str, session_id: str, model: str = "llama3") -> Dict[str, Any]:
        """
        Generate response from Ollama.
        
        Args:
            prompt: Prompt with context
            session_id: Session ID
            model: Ollama model to use
            
        Returns:
            Dictionary with response
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": model, "prompt": prompt}
            )
            data = response.json()
            return {
                "response": data.get("response", ""),
                "type": "llm_response"
            }
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return {
                "response": f"Error generating response: {e}",
                "type": "error"
            }
    
    def _update_history(self, session_id: str, role: str, content: str) -> None:
        """
        Update session history.
        
        Args:
            session_id: Session ID
            role: Message role (user or assistant)
            content: Message content
        """
        try:
            # Get current session context
            response = requests.get(
                f"{self.continuity_url}/session/{session_id}"
            )
            context = response.json()
            
            # Ensure history exists
            if "history" not in context:
                context["history"] = []
            
            # Add entry
            context["history"].append({
                "type": role,
                "content": content,
                "timestamp": self._get_timestamp()
            })
            
            # Update session context
            requests.post(
                f"{self.continuity_url}/session/update",
                json={
                    "session_id": session_id,
                    "context_update": {"history": context["history"]}
                }
            )
        except Exception as e:
            self.logger.error(f"Error updating history: {e}")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def list_models(self) -> List[str]:
        """
        List available Ollama models.
        
        Returns:
            List of model names
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        except Exception as e:
            self.logger.error(f"Error listing models: {e}")
            return []
