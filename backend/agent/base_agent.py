"""
Base Agent Definitions for AIDEN V2

Contains the StreamingAgent class and Gemini model creation utilities.
"""
import logging
import json
import asyncio
from typing import Optional, AsyncGenerator, Dict, Any, List
import os

from agno.agent import Agent
from agno.models.google import Gemini

from backend.config import settings as global_settings # Renamed to avoid conflict

logger = logging.getLogger(__name__)

class StreamingAgent(Agent):
    """Extended Agno Agent class with streaming capabilities for AIDEN."""

    async def stream_run(self, prompt: str, session_id: str = "default") -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream the execution of the agent, yielding events for tool usage and responses.
        
        Args:
            prompt: User prompt to process.
            session_id: Identifier for the current session (for memory, logging, etc.).
            
        Yields:
            Event dictionaries with types:
            - tool_start: When a tool starts executing
            - tool_end: When a tool completes execution
            - llm_chunk: Chunks of LLM output
            - final_response: The final response from the agent
            - error: If an error occurs
            - thinking_indicator: Signals agent is processing
        """
        logger.info(f"[Session: {session_id}] Starting streaming agent run for prompt: '{prompt[:50]}...'")
        
        try:
            yield {"type": "thinking_indicator", "content": "Analyzing request..."}

            search_performed_results = None
            if self.tools and global_settings.ENABLE_WEB_SEARCH and await self._needs_web_search(prompt):
                yield {"type": "thinking_indicator", "content": "Searching the web..."}
                web_search_tool = next((t for t in self.tools if hasattr(t, 'search') and t.__class__.__name__ == "DuckDuckGoTools"), None)
                
                if web_search_tool:
                    search_query = self._extract_search_query(prompt)
                    tool_name = web_search_tool.__class__.__name__
                    
                    yield {"type": "tool_start", "name": tool_name, "input": search_query}
                    try:
                        search_results = web_search_tool.search(search_query)
                        search_performed_results = search_results
                        yield {
                            "type": "tool_end", 
                            "name": tool_name, 
                            "result": json.dumps(search_results, default=str)[:1000]
                        }
                    except Exception as e:
                        logger.error(f"[Session: {session_id}] Web search with {tool_name} failed: {e}", exc_info=True)
                        yield {"type": "error", "name": tool_name, "detail": str(e)}
                else:
                    logger.warning(f"[Session: {session_id}] Web search enabled, but no suitable search tool found.")

            current_prompt = prompt
            if search_performed_results:
                current_prompt = self._add_search_context_to_prompt(prompt, search_performed_results)
                yield {"type": "thinking_indicator", "content": "Incorporating search results..."}

            yield {"type": "thinking_indicator", "content": "Generating response..."}
            
            # Implement actual token-by-token streaming
            full_response = ""
            streaming_successful = False
            
            try:
                # Try multiple approaches to access streaming capabilities
                
                # Approach 1: Check if model has a direct client attribute
                if hasattr(self.model, 'client') and self.model.client:
                    logger.debug(f"[Session: {session_id}] Attempting streaming via model.client")
                    try:
                        response = self.model.client.generate_content(
                            current_prompt,
                            stream=True
                        )
                        
                        for chunk in response:
                            if hasattr(chunk, 'text') and chunk.text:
                                chunk_text = chunk.text
                                full_response += chunk_text
                                yield {"type": "llm_chunk", "content": chunk_text}
                                await asyncio.sleep(0.01)
                        
                        streaming_successful = True
                        logger.debug(f"[Session: {session_id}] Streaming via model.client successful")
                    except Exception as e:
                        logger.debug(f"[Session: {session_id}] Streaming via model.client failed: {e}")
                
                # Approach 2: Try direct Google GenerativeAI client
                if not streaming_successful:
                    logger.debug(f"[Session: {session_id}] Attempting streaming via google.generativeai")
                    try:
                        import google.generativeai as genai
                        
                        # Configure with API key
                        genai.configure(api_key=global_settings.GOOGLE_API_KEY)
                        
                        # Get the model
                        model = genai.GenerativeModel(global_settings.GEMINI_MODEL_ID)
                        
                        # Stream the response
                        response = model.generate_content(
                            current_prompt,
                            stream=True
                        )
                        
                        for chunk in response:
                            if hasattr(chunk, 'text') and chunk.text:
                                chunk_text = chunk.text
                                full_response += chunk_text
                                yield {"type": "llm_chunk", "content": chunk_text}
                                await asyncio.sleep(0.01)
                        
                        streaming_successful = True
                        logger.debug(f"[Session: {session_id}] Streaming via google.generativeai successful")
                    except ImportError:
                        logger.debug(f"[Session: {session_id}] google.generativeai not available")
                    except Exception as e:
                        logger.debug(f"[Session: {session_id}] Streaming via google.generativeai failed: {e}")
                
                # Approach 3: Check if model has a generate_stream method
                if not streaming_successful and hasattr(self.model, 'generate_stream'):
                    logger.debug(f"[Session: {session_id}] Attempting streaming via model.generate_stream")
                    try:
                        stream = self.model.generate_stream(current_prompt)
                        for chunk in stream:
                            if hasattr(chunk, 'content') and chunk.content:
                                chunk_text = chunk.content
                                full_response += chunk_text
                                yield {"type": "llm_chunk", "content": chunk_text}
                                await asyncio.sleep(0.01)
                        
                        streaming_successful = True
                        logger.debug(f"[Session: {session_id}] Streaming via model.generate_stream successful")
                    except Exception as e:
                        logger.debug(f"[Session: {session_id}] Streaming via model.generate_stream failed: {e}")
                
                # Fallback: Simulate streaming if no direct streaming available
                if not streaming_successful:
                    logger.warning(f"[Session: {session_id}] No direct streaming available, simulating with word chunks")
                    
                    # Get the full response first
                    final_agent_response = self.run(current_prompt)
                    
                    if hasattr(final_agent_response, 'content'):
                        response_content = final_agent_response.content
                    elif isinstance(final_agent_response, str):
                        response_content = final_agent_response
                    else:
                        response_content = str(final_agent_response)
                    
                    # Simulate streaming by chunking the response word by word
                    words = response_content.split()
                    chunk_size = 2  # Stream 2 words at a time for better visual effect
                    
                    for i in range(0, len(words), chunk_size):
                        chunk_words = words[i:i + chunk_size]
                        chunk_text = " ".join(chunk_words)
                        if i + chunk_size < len(words):
                            chunk_text += " "
                        
                        full_response += chunk_text
                        yield {"type": "llm_chunk", "content": chunk_text}
                        await asyncio.sleep(0.05)  # Slower delay for visible streaming effect
                
                # Send final response
                yield {"type": "final_response", "content": full_response}
                
            except Exception as e:
                logger.error(f"[Session: {session_id}] Error during LLM streaming: {e}", exc_info=True)
                
                # Ultimate fallback to non-streaming response
                logger.warning(f"[Session: {session_id}] Falling back to non-streaming response")
                try:
                    final_agent_response = self.run(current_prompt)
                    
                    if hasattr(final_agent_response, 'content'):
                        response_content = final_agent_response.content
                    elif isinstance(final_agent_response, str):
                        response_content = final_agent_response
                    else:
                        response_content = str(final_agent_response)
                    
                    yield {"type": "llm_chunk", "content": response_content}
                    yield {"type": "final_response", "content": response_content}
                except Exception as fallback_error:
                    logger.error(f"[Session: {session_id}] Even fallback response failed: {fallback_error}", exc_info=True)
                    yield {"type": "error", "detail": f"Failed to generate response: {str(fallback_error)}"}
            
            logger.info(f"[Session: {session_id}] Streaming agent run completed successfully.")
            
        except Exception as e:
            logger.error(f"[Session: {session_id}] Error during streaming agent run: {e}", exc_info=True)
            yield {"type": "error", "detail": f"An unexpected error occurred: {str(e)}"}

    async def _needs_web_search(self, prompt: str) -> bool:
        prompt_lower = prompt.lower()
        search_keywords = [
            "latest news", "current events", "what is the weather", "define", "who is", 
            "what is", "how to", "search for", "find information on", "stock price",
            "recent updates", "statistics for", "release date"
        ]
        if any(keyword in prompt_lower for keyword in search_keywords):
            return True
        if "?" in prompt and len(prompt.split()) > 5:
            return True
        return False

    def _extract_search_query(self, prompt: str) -> str:
        if len(prompt) < 100:
            return prompt 
        return prompt[:150] + "..." if len(prompt) > 150 else prompt

    def _add_search_context_to_prompt(self, prompt: str, search_results: Any) -> str:
        context_str = "\n\nRelevant information from web search (use this to answer the query):\n"
        if isinstance(search_results, list) and search_results:
            for i, res in enumerate(search_results[:3]):
                title = res.get('title', 'N/A')
                snippet = res.get('snippet', res.get('body', 'N/A'))
                url = res.get('href', res.get('link', 'N/A'))
                context_str += f"{i+1}. Title: {title}\n   Snippet: {snippet[:200]}...\n   Source: {url}\n"
        elif isinstance(search_results, str):
            context_str += search_results[:1000]
        elif search_results:
             context_str += str(search_results)[:1000]
        else:
            return prompt
        return f"{prompt}{context_str}\n\nBased on the information above, please answer the original query."


def create_gemini_model(model_id: Optional[str] = None, api_key: Optional[str] = None) -> Gemini:
    resolved_api_key = api_key or global_settings.GOOGLE_API_KEY
    resolved_model_id = model_id or global_settings.GEMINI_MODEL_ID

    # Need a way to validate the API key without creating a full Settings instance if an API key is passed directly.
    # For now, we rely on the global_settings.is_google_api_key_valid for the settings-derived key,
    # and a basic check for a directly passed key.
    key_to_validate = resolved_api_key
    is_valid_passed_key = bool(key_to_validate and not key_to_validate.startswith("your") and len(key_to_validate) > 20)

    if not ( (api_key and is_valid_passed_key) or (not api_key and global_settings.is_google_api_key_valid) ):
        logger.error("Google API Key is not set or appears invalid.")
        raise ValueError("Google API Key is not set or invalid. Please check your .env file or configuration.")
    
    logger.info(f"Initializing Gemini model: {resolved_model_id}")
    return Gemini(
        id=resolved_model_id,
        api_key=resolved_api_key
    ) 