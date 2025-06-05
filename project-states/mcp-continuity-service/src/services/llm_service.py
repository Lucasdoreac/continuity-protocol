"""
LLM Service - Integration with local and remote LLMs
Supports multiple LLM providers including local models
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, AsyncGenerator
from pathlib import Path
import logging
from abc import ABC, abstractmethod

# Local LLM integrations
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

# Remote LLM integrations
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class BaseLLMProvider(ABC):
    """Base class for LLM providers"""
    
    @abstractmethod
    async def chat_completion(self, messages: List[Dict], **kwargs) -> AsyncGenerator[str, None]:
        pass
    
    @abstractmethod
    async def inject_continuity_context(self, messages: List[Dict], context: Dict) -> List[Dict]:
        pass


class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider"""
    
    def __init__(self, model_name: str = "llama3.2:latest", host: str = "localhost:11434"):
        if not OLLAMA_AVAILABLE:
            raise ImportError("Ollama not available. Install with: pip install ollama")
        
        self.model_name = model_name
        self.host = host
        self.client = ollama.Client(host=host)
        self.logger = logging.getLogger(__name__)
    
    async def chat_completion(self, messages: List[Dict], **kwargs) -> AsyncGenerator[str, None]:
        """Stream chat completion from Ollama"""
        try:
            # Convert messages to Ollama format
            prompt = self._messages_to_prompt(messages)
            
            # Stream response
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                stream=True
            )
            
            for chunk in response:
                if chunk.get('response'):
                    yield chunk['response']
                    
        except Exception as e:
            self.logger.error(f"Ollama completion error: {e}")
            yield f"Error: {str(e)}"
    
    async def inject_continuity_context(self, messages: List[Dict], context: Dict) -> List[Dict]:
        """Inject continuity context into system prompt"""
        if not context or not messages:
            return messages
        
        # Create continuity system message
        continuity_prompt = f"""
CONTINUIDADE AUTOMÁTICA ATIVADA:

CONTEXTO DA SESSÃO ANTERIOR:
{json.dumps(context, indent=2, ensure_ascii=False)}

INSTRUÇÕES DE CONTINUIDADE:
- Se o usuário perguntar "onde paramos?" ou similar, use o contexto acima
- Apresente projetos ativos, missões críticas e próximas ações
- Mantenha a continuidade natural da conversa
- Execute recovery automático se necessário
"""
        
        # Inject into system message or create new one
        if messages and messages[0].get('role') == 'system':
            messages[0]['content'] = f"{messages[0]['content']}\n\n{continuity_prompt}"
        else:
            messages.insert(0, {'role': 'system', 'content': continuity_prompt})
        
        return messages
    
    def _messages_to_prompt(self, messages: List[Dict]) -> str:
        """Convert chat messages to single prompt"""
        prompt_parts = []
        
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            
            if role == 'system':
                prompt_parts.append(f"System: {content}")
            elif role == 'user':
                prompt_parts.append(f"Human: {content}")
            elif role == 'assistant':
                prompt_parts.append(f"Assistant: {content}")
        
        prompt_parts.append("Assistant:")
        return "\n\n".join(prompt_parts)


class TransformersProvider(BaseLLMProvider):
    """Local transformers model provider"""
    
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium", device: str = "auto"):
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("Transformers not available. Install with: pip install transformers torch")
        
        self.model_name = model_name
        self.device = device
        self.tokenizer = None
        self.model = None
        self.logger = logging.getLogger(__name__)
        
    async def load_model(self):
        """Load model and tokenizer"""
        if self.model is None:
            self.logger.info(f"Loading model: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            
            if self.device == "auto":
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
            
            self.model.to(self.device)
    
    async def chat_completion(self, messages: List[Dict], **kwargs) -> AsyncGenerator[str, None]:
        """Generate completion using transformers"""
        await self.load_model()
        
        try:
            # Convert messages to input text
            input_text = self._messages_to_text(messages)
            
            # Tokenize
            inputs = self.tokenizer.encode(input_text, return_tensors="pt").to(self.device)
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + kwargs.get('max_tokens', 150),
                    do_sample=True,
                    temperature=kwargs.get('temperature', 0.7),
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
            yield response.strip()
            
        except Exception as e:
            self.logger.error(f"Transformers completion error: {e}")
            yield f"Error: {str(e)}"
    
    async def inject_continuity_context(self, messages: List[Dict], context: Dict) -> List[Dict]:
        """Inject continuity context"""
        # Similar to Ollama implementation
        return messages
    
    def _messages_to_text(self, messages: List[Dict]) -> str:
        """Convert messages to text input"""
        return "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages[-5:]])  # Last 5 messages


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider"""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI not available. Install with: pip install openai")
        
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.model = model
        self.logger = logging.getLogger(__name__)
    
    async def chat_completion(self, messages: List[Dict], **kwargs) -> AsyncGenerator[str, None]:
        """Stream chat completion from OpenAI"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                **kwargs
            )
            
            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            self.logger.error(f"OpenAI completion error: {e}")
            yield f"Error: {str(e)}"
    
    async def inject_continuity_context(self, messages: List[Dict], context: Dict) -> List[Dict]:
        """Inject continuity context into system prompt"""
        # Similar to Ollama implementation but optimized for OpenAI
        return messages


class LLMService:
    """Main LLM service that manages multiple providers"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.providers: Dict[str, BaseLLMProvider] = {}
        self.default_provider = self.config.get('default_provider', 'ollama')
        self.logger = logging.getLogger(__name__)
        
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available providers based on configuration"""
        
        # Ollama (local)
        if OLLAMA_AVAILABLE and self.config.get('ollama', {}).get('enabled', True):
            try:
                self.providers['ollama'] = OllamaProvider(
                    model_name=self.config.get('ollama', {}).get('model', 'llama3.2:latest'),
                    host=self.config.get('ollama', {}).get('host', 'localhost:11434')
                )
                self.logger.info("Ollama provider initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Ollama: {e}")
        
        # Transformers (local)
        if TRANSFORMERS_AVAILABLE and self.config.get('transformers', {}).get('enabled', False):
            try:
                self.providers['transformers'] = TransformersProvider(
                    model_name=self.config.get('transformers', {}).get('model', 'microsoft/DialoGPT-medium')
                )
                self.logger.info("Transformers provider initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Transformers: {e}")
        
        # OpenAI (remote)
        if OPENAI_AVAILABLE and self.config.get('openai', {}).get('api_key'):
            try:
                self.providers['openai'] = OpenAIProvider(
                    api_key=self.config['openai']['api_key'],
                    model=self.config.get('openai', {}).get('model', 'gpt-3.5-turbo')
                )
                self.logger.info("OpenAI provider initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize OpenAI: {e}")
    
    async def chat_with_continuity(
        self,
        messages: List[Dict],
        session_id: str,
        provider: Optional[str] = None,
        continuity_context: Optional[Dict] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Chat with continuity context injection"""
        
        provider_name = provider or self.default_provider
        
        if provider_name not in self.providers:
            yield f"Error: Provider '{provider_name}' not available"
            return
        
        llm_provider = self.providers[provider_name]
        
        # Inject continuity context if provided
        if continuity_context:
            messages = await llm_provider.inject_continuity_context(messages, continuity_context)
        
        # Generate response
        async for chunk in llm_provider.chat_completion(messages, **kwargs):
            yield chunk
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(self.providers.keys())
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all providers"""
        health = {}
        
        for name, provider in self.providers.items():
            try:
                # Simple test message
                test_messages = [{"role": "user", "content": "Hello"}]
                response_chunks = []
                
                async for chunk in provider.chat_completion(test_messages):
                    response_chunks.append(chunk)
                    if len("".join(response_chunks)) > 10:  # Just need a small response
                        break
                
                health[name] = {
                    "status": "healthy",
                    "response_length": len("".join(response_chunks))
                }
            except Exception as e:
                health[name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return health
