"""
OpenRouter Model Implementation for Agno

Provides access to OpenRouter models, specifically optimized for the new
Llama 4 Maverick free model for fastest performance.
"""

import logging
import os
from typing import Optional, Dict, Any, AsyncGenerator, List, Union
import httpx
import json

from agno.models.base import Model

logger = logging.getLogger(__name__)


class OpenRouterModel(Model):
    """
    OpenRouter model implementation for Agno.
    
    Optimized for the new Llama 4 Maverick free model which offers
    industry-leading performance at minimal cost.
    """

    def __init__(
        self,
        id: str = "meta-llama/llama-4-maverick:free",  # Default to fastest free model
        api_key: Optional[str] = None,
        base_url: str = "https://openrouter.ai/api/v1",
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        top_p: float = 0.9,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        **kwargs
    ):
        """
        Initialize OpenRouter model.
        
        Args:
            id: Model ID (default: meta-llama/llama-4-maverick:free)
            api_key: OpenRouter API key
            base_url: OpenRouter API base URL
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            frequency_penalty: Frequency penalty
            presence_penalty: Presence penalty
            **kwargs: Additional parameters
        """
        # Call parent class with required id parameter
        super().__init__(id=id)
        
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key is required")
        
        self.base_url = base_url
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        
        # Additional OpenRouter specific parameters
        self.extra_params = kwargs
        
        # HTTP client configuration
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/agno-agi/agno",  # Optional: for analytics
                "X-Title": "AIDEN V2"  # Optional: for analytics
            },
            timeout=60.0
        )
        
        logger.info(f"Initialized OpenRouter model: {self.id}")

    # Required abstract methods from Agno Model base class
    async def ainvoke(self, messages: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        Async invoke method required by Agno Model base class.
        
        Args:
            messages: List of chat messages
            **kwargs: Additional parameters
            
        Returns:
            Model response dictionary
        """
        try:
            # Prepare request payload
            payload = {
                "model": self.id,
                "messages": messages,
                "temperature": kwargs.get("temperature", self.temperature),
                "top_p": kwargs.get("top_p", self.top_p),
                "frequency_penalty": kwargs.get("frequency_penalty", self.frequency_penalty),
                "presence_penalty": kwargs.get("presence_penalty", self.presence_penalty),
                "stream": False
            }
            
            if self.max_tokens:
                payload["max_tokens"] = kwargs.get("max_tokens", self.max_tokens)
            
            # Add extra parameters
            payload.update(self.extra_params)
            payload.update(kwargs)
            
            logger.debug(f"Sending request to OpenRouter: {self.id}")
            
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from OpenRouter: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error in ainvoke: {e}")
            raise

    async def ainvoke_stream(self, messages: List[Dict[str, Any]], **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Async invoke stream method required by Agno Model base class.
        
        Args:
            messages: List of chat messages
            **kwargs: Additional parameters
            
        Yields:
            Model response chunks
        """
        try:
            # Prepare request payload
            payload = {
                "model": self.id,
                "messages": messages,
                "temperature": kwargs.get("temperature", self.temperature),
                "top_p": kwargs.get("top_p", self.top_p),
                "frequency_penalty": kwargs.get("frequency_penalty", self.frequency_penalty),
                "presence_penalty": kwargs.get("presence_penalty", self.presence_penalty),
                "stream": True
            }
            
            if self.max_tokens:
                payload["max_tokens"] = kwargs.get("max_tokens", self.max_tokens)
            
            # Add extra parameters
            payload.update(self.extra_params)
            payload.update(kwargs)
            
            logger.debug(f"Starting stream from OpenRouter: {self.id}")
            
            async with self.client.stream("POST", "/chat/completions", json=payload) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix
                        
                        if data.strip() == "[DONE]":
                            break
                        
                        try:
                            chunk = json.loads(data)
                            yield chunk
                                    
                        except json.JSONDecodeError:
                            continue
                            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from OpenRouter streaming: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"Error in ainvoke_stream: {e}")
            raise

    def invoke(self, messages: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        Sync invoke method required by Agno Model base class.
        
        Args:
            messages: List of chat messages
            **kwargs: Additional parameters
            
        Returns:
            Model response dictionary
        """
        # For sync version, we'll use the httpx sync client
        try:
            # Create a sync client for this request
            with httpx.Client(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/agno-agi/agno",
                    "X-Title": "AIDEN V2"
                },
                timeout=60.0
            ) as client:
                # Prepare request payload
                payload = {
                    "model": self.id,
                    "messages": messages,
                    "temperature": kwargs.get("temperature", self.temperature),
                    "top_p": kwargs.get("top_p", self.top_p),
                    "frequency_penalty": kwargs.get("frequency_penalty", self.frequency_penalty),
                    "presence_penalty": kwargs.get("presence_penalty", self.presence_penalty),
                    "stream": False
                }
                
                if self.max_tokens:
                    payload["max_tokens"] = kwargs.get("max_tokens", self.max_tokens)
                
                # Add extra parameters
                payload.update(self.extra_params)
                payload.update(kwargs)
                
                logger.debug(f"Sending sync request to OpenRouter: {self.id}")
                
                response = client.post("/chat/completions", json=payload)
                response.raise_for_status()
                
                result = response.json()
                return result
                    
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from OpenRouter sync: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error in invoke: {e}")
            raise

    def invoke_stream(self, messages: List[Dict[str, Any]], **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Sync invoke stream method required by Agno Model base class.
        Note: This returns an async generator even though it's the "sync" version.
        
        Args:
            messages: List of chat messages
            **kwargs: Additional parameters
            
        Yields:
            Model response chunks
        """
        # For consistency with Agno's expected interface, we'll return the async version
        return self.ainvoke_stream(messages, **kwargs)

    def parse_provider_response(self, response: Dict[str, Any]) -> str:
        """
        Parse provider response required by Agno Model base class.
        
        Args:
            response: Raw response from OpenRouter API
            
        Returns:
            Parsed text content
        """
        try:
            if "choices" in response and len(response["choices"]) > 0:
                choice = response["choices"][0]
                if "message" in choice and "content" in choice["message"]:
                    return choice["message"]["content"]
                elif "text" in choice:
                    return choice["text"]
            
            logger.error(f"Unexpected response format: {response}")
            return ""
            
        except Exception as e:
            logger.error(f"Error parsing provider response: {e}")
            return ""

    def parse_provider_response_delta(self, delta: Dict[str, Any]) -> Optional[str]:
        """
        Parse provider response delta for streaming required by Agno Model base class.
        
        Args:
            delta: Delta chunk from streaming response
            
        Returns:
            Parsed text content or None
        """
        try:
            if "choices" in delta and len(delta["choices"]) > 0:
                choice = delta["choices"][0]
                if "delta" in choice and "content" in choice["delta"]:
                    return choice["delta"]["content"]
                elif "text" in choice:
                    return choice["text"]
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing provider response delta: {e}")
            return None

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate text using OpenRouter API.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text
        """
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            response = await self.ainvoke(messages, **kwargs)
            return self.parse_provider_response(response)
                
        except Exception as e:
            logger.error(f"Error generating with OpenRouter: {e}")
            raise

    async def stream_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Stream generate text using OpenRouter API.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            **kwargs: Additional generation parameters
            
        Yields:
            Text chunks
        """
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            async for delta in self.ainvoke_stream(messages, **kwargs):
                content = self.parse_provider_response_delta(delta)
                if content:
                    yield content
                            
        except Exception as e:
            logger.error(f"Error streaming from OpenRouter: {e}")
            raise

    async def generate_with_tools(
        self,
        prompt: str,
        tools: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate with function calling support if the model supports it.
        
        Args:
            prompt: User prompt
            tools: List of tool definitions
            system_prompt: Optional system prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Response with potential tool calls
        """
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            # Add tools if the model supports function calling
            if tools and self._supports_function_calling():
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"
            
            logger.debug(f"Sending tools request to OpenRouter: {self.id}")
            
            response = await self.ainvoke(messages, **kwargs)
            return response
            
        except Exception as e:
            logger.error(f"Error generating with tools: {e}")
            raise

    def _supports_function_calling(self) -> bool:
        """Check if the current model supports function calling."""
        # Llama 4 models support function calling
        function_calling_models = [
            "meta-llama/llama-4-maverick",
            "meta-llama/llama-4-scout",
            "meta-llama/llama-4-behemoth"
        ]
        
        return any(model in self.id for model in function_calling_models)

    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        try:
            response = await self.client.get("/models")
            response.raise_for_status()
            
            models = response.json()
            
            for model in models.get("data", []):
                if model["id"] == self.id:
                    return model
            
            return {"id": self.id, "info": "Model information not found"}
            
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {"id": self.id, "error": str(e)}

    async def list_available_models(self) -> List[Dict[str, Any]]:
        """List all available models on OpenRouter."""
        try:
            response = await self.client.get("/models")
            response.raise_for_status()
            
            result = response.json()
            return result.get("data", [])
            
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []

    async def close(self):
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()

    def __del__(self):
        """Cleanup when object is destroyed."""
        try:
            import asyncio
            if self.client and not self.client.is_closed:
                # Try to close cleanly if possible
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.client.aclose())
                else:
                    asyncio.run(self.client.aclose())
        except Exception:
            pass  # Ignore cleanup errors 