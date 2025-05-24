"""
Agent factory module for creating optimized Agno agents
"""
import os
import json
import asyncio
from typing import Optional, AsyncGenerator, Dict, Any
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
import logging
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Extend the Agent class to add streaming capability
class StreamingAgent(Agent):
    """Extended Agent class with streaming capabilities"""
    
    async def stream_run(self, prompt: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream the execution of the agent, yielding events for tool usage and responses.
        
        Args:
            prompt: User prompt to process
            
        Yields:
            Event dictionaries with types:
            - tool_start: When a tool starts executing
            - tool_end: When a tool completes execution
            - llm_chunk: Chunks of LLM output (if supported)
            - final_response: The final response from the agent
            - error: If an error occurs
        """
        logger.info("Starting streaming agent run")
        
        try:
            # If web search is enabled and there are tools
            if self.tools and settings.ENABLE_WEB_SEARCH:
                # Start thinking process
                yield {"type": "llm_chunk", "content": "Thinking..."}
                
                # Check if the prompt might need web search
                needs_search = await self._check_if_needs_search(prompt)
                
                if needs_search:
                    # Execute web search
                    for tool in self.tools:
                        if hasattr(tool, 'search'):
                            tool_name = tool.__class__.__name__
                            search_query = self._extract_search_query(prompt)
                            
                            # Yield tool start event
                            yield {
                                "type": "tool_start",
                                "name": "web_search",
                                "input": search_query
                            }
                            
                            try:
                                # Perform the actual search
                                search_results = tool.search(search_query)
                                
                                # Yield tool end event with results
                                yield {
                                    "type": "tool_end",
                                    "name": "web_search",
                                    "result": json.dumps(search_results, default=str)[:1000] + "..." if len(json.dumps(search_results, default=str)) > 1000 else json.dumps(search_results, default=str)
                                }
                                
                                # Add search context to prompt
                                prompt = self._add_search_context(prompt, search_results)
                                
                            except Exception as e:
                                logger.error(f"Search failed: {e}")
                                yield {
                                    "type": "error",
                                    "detail": f"Search failed: {str(e)}",
                                    "name": "web_search"
                                }
            
            # Provide thinking indicator
            yield {"type": "llm_chunk", "content": "Processing response..."}
            await asyncio.sleep(0.5)  # Brief pause for UI
            
            # Get the final response from the model
            response = self.run(prompt)
            
            # Yield the final response
            yield {
                "type": "final_response",
                "content": response.content
            }
            
            logger.info("Streaming agent run completed successfully")
            
        except Exception as e:
            logger.error(f"Streaming agent error: {e}")
            yield {
                "type": "error",
                "detail": f"Error processing request: {str(e)}"
            }
    
    async def _check_if_needs_search(self, prompt: str) -> bool:
        """Simple heuristic to check if a prompt might need web search"""
        # For simplicity, let's check for keywords indicating need for search
        search_indicators = [
            "search", "look up", "find information", "latest", "current", 
            "recent", "news", "what is", "who is", "how to", "when", "where"
        ]
        prompt_lower = prompt.lower()
        
        return any(indicator in prompt_lower for indicator in search_indicators)
    
    def _extract_search_query(self, prompt: str) -> str:
        """Extract a search query from the prompt - simplified version"""
        # For simplicity, just use the prompt as search query
        # In a real implementation, LLM could extract specific search terms
        return prompt[:100] + "..." if len(prompt) > 100 else prompt
    
    def _add_search_context(self, prompt: str, search_results) -> str:
        """Add search results as context to the prompt"""
        search_context = "\nSearch results:\n"
        
        # Format the search results depending on their structure
        if isinstance(search_results, list):
            for i, result in enumerate(search_results[:3]):  # Limit to first 3 results
                if isinstance(result, dict):
                    title = result.get('title', 'Untitled')
                    snippet = result.get('snippet', 'No snippet available')
                    url = result.get('url', 'No URL available')
                    search_context += f"{i+1}. {title}\nSnippet: {snippet}\nURL: {url}\n\n"
                else:
                    search_context += f"{i+1}. {str(result)}\n"
        else:
            search_context += str(search_results)
            
        return f"{prompt}\n{search_context}\nPlease use the above search results to help answer the query."

def create_gemini_model() -> Gemini:
    """Create a Gemini model instance with proper configuration"""
    if not settings.is_api_key_valid:
        raise ValueError("GOOGLE_API_KEY is not set or invalid")
    
    return Gemini(
        id=settings.GEMINI_MODEL_ID,
        api_key=settings.GOOGLE_API_KEY
    )

def create_agent() -> StreamingAgent:
    """Create and return an optimized Gemini agent with search capabilities"""
    try:
        model = create_gemini_model()
        tools = [DuckDuckGoTools()] if settings.ENABLE_WEB_SEARCH else []
        
        agent = StreamingAgent(
            model=model,
            tools=tools,
            instructions=[
                "You are a helpful AI assistant powered by Gemini 2.5 Flash Preview.",
                "You can search the web for current information when needed, but if search fails due to rate limits, provide helpful responses based on your knowledge.",
                "Always provide accurate, helpful, and well-structured responses.",
                "If you encounter search errors, acknowledge them briefly and provide the best answer you can from your training data.",
                "Be conversational and helpful in all interactions.",
                "Format your responses in markdown when appropriate for better readability.",
            ],
            show_tool_calls=settings.SHOW_TOOL_CALLS,
            markdown=settings.ENABLE_MARKDOWN,
        )
        
        logger.info(f"Agent created successfully with {len(tools)} tools")
        return agent
        
    except Exception as e:
        logger.error(f"Failed to create agent: {e}")
        raise

def create_simple_agent() -> StreamingAgent:
    """Create a basic agent without web search for testing"""
    try:
        model = create_gemini_model()
        
        agent = StreamingAgent(
            model=model,
            instructions=[
                "You are a helpful AI assistant powered by Gemini 2.5 Flash Preview.",
                "Provide accurate, helpful, and well-structured responses.",
                "Be conversational and engaging in all interactions.",
                "Format your responses in markdown when appropriate for better readability.",
            ],
            show_tool_calls=settings.SHOW_TOOL_CALLS,
            markdown=settings.ENABLE_MARKDOWN,
        )
        
        logger.info("Simple agent created successfully (no web search)")
        return agent
        
    except Exception as e:
        logger.error(f"Failed to create simple agent: {e}")
        raise

def create_agent_with_fallback() -> Optional[StreamingAgent]:
    """Create agent with automatic fallback to simple agent if needed"""
    try:
        return create_agent()
    except Exception as e:
        logger.warning(f"Failed to create agent with web search: {e}")
        logger.info("Falling back to simple agent...")
        try:
            return create_simple_agent()
        except Exception as e2:
            logger.error(f"Failed to create fallback agent: {e2}")
            return None

# Test the agent locally
if __name__ == "__main__":
    # Make sure to set your GOOGLE_API_KEY environment variable
    if not os.getenv("GOOGLE_API_KEY"):
        print("Please set your GOOGLE_API_KEY environment variable")
        exit(1)
    
    agent = create_agent()
    
    # Test the agent
    response = agent.run("Hello! Can you tell me about the latest developments in AI?")
    print(response.content) 