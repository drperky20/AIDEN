"""
AIDEN V2 API Routes

Defines the API endpoints for chat, streaming, health checks, and other interactions.
"""
import logging
import json
import asyncio
from typing import Dict, Any, List, Optional, AsyncGenerator

from fastapi import APIRouter, Form, HTTPException, Depends, Query, Body
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field

from backend.config import settings
from backend.core.memory import memory_manager
from backend.agent.agent_factory import get_agent_instance # To get the initialized agent
from backend.agent.base_agent import StreamingAgent # For type hinting

logger = logging.getLogger(__name__)
router = APIRouter() # Main router for the API

# --- Request Models --- #
class ChatMessageInput(BaseModel):
    message: str = Field(..., description="The user's message to the agent.", min_length=1)
    session_id: Optional[str] = Field("default", description="Identifier for the conversation session.")
    # Potentially add other parameters like temperature, specific agent_id if multiple are served, etc.

# --- Helper Functions --- #
async def get_current_active_agent() -> StreamingAgent:
    """Dependency to get the currently active (initialized) agent instance."""
    try:
        return get_agent_instance()
    except RuntimeError as e:
        logger.error(f"Agent not available: {e}")
        raise HTTPException(
            status_code=503, 
            detail="AIDEN agent is not currently available. Please try again later or contact support."
        )

# --- API Endpoints --- #

@router.post("/chat", tags=["Chat"], summary="Send a message to the agent (non-streaming)")
async def chat_endpoint(
    payload: ChatMessageInput = Body(...),
    agent: StreamingAgent = Depends(get_current_active_agent)
) -> Dict[str, Any]:
    """
    Handles a single chat message and returns a complete response from the agent.
    Conversation history is automatically retrieved and prepended to the prompt.
    """
    logger.info(f"[/chat] Received message for session '{payload.session_id}': '{payload.message[:50]}...'")
    
    try:
        history_context = await memory_manager.get_formatted_conversation_history(
            session_id=payload.session_id, 
            limit=settings.MAX_HISTORY_MESSAGES
        )
        
        full_prompt = payload.message.strip()
        if history_context:
            full_prompt = f"{history_context}\n\nUser: {payload.message.strip()}"
            logger.debug(f"[/chat] Using context of {len(history_context.splitlines())} lines for session '{payload.session_id}'.")

        # The agent.run() is synchronous in the current Agno structure for StreamingAgent
        # If Agno's agent.run() becomes async, this should be awaited.
        response_obj = agent.run(full_prompt) 
        
        agent_response_content = getattr(response_obj, 'content', str(response_obj))
        
        await memory_manager.add_conversation_turn(
            session_id=payload.session_id,
            user_message=payload.message.strip(), 
            agent_response=agent_response_content
        )
        
        return {
            "session_id": payload.session_id,
            "response": agent_response_content,
            "success": True,
            "message_length": len(agent_response_content)
        }
        
    except HTTPException: # Re-raise HTTPExceptions directly
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"[/chat] Error processing message for session '{payload.session_id}': {error_msg}", exc_info=True)
        
        # Basic check for rate limiting type errors from LLM provider
        if any(keyword in error_msg.lower() for keyword in ["rate limit", "ratelimit", "quota exceeded", "429"]):
            raise HTTPException(status_code=429, detail="The AI model is currently experiencing high demand (rate limit). Please try again shortly.")
        
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while processing your message: {error_msg}")

async def sse_event_generator(prompt: str, session_id: str, agent_instance: StreamingAgent) -> AsyncGenerator[str, None]:
    """
    Server-Sent Events (SSE) generator for streaming agent responses.
    Yields events from the agent's `stream_run` method.
    """
    logger.debug(f"[SSE] Starting event generator for session '{session_id}'.")
    full_response_content = ""
    last_event_data = None

    try:
        async for event_data in agent_instance.stream_run(prompt, session_id=session_id):
            last_event_data = event_data # Keep track of the last event for DB saving
            yield f"data: {json.dumps(event_data)}\n\n"
            await asyncio.sleep(0.01) # Small sleep to ensure event flushing

            if event_data.get("type") == "llm_chunk" and "content" in event_data:
                full_response_content += event_data["content"]
            elif event_data.get("type") == "final_response" and "content" in event_data:
                full_response_content = event_data["content"] # final_response overrides chunks
        
        # After the stream finishes, save the conversation if a response was generated and no critical error occurred
        if full_response_content and not (last_event_data and last_event_data.get("type") == "error" and last_event_data.get("critical")):
            await memory_manager.add_conversation_turn(
                session_id=session_id,
                user_message=prompt.split("\n\nUser:")[-1].strip() if "\n\nUser:" in prompt else prompt, # Extract original user msg
                agent_response=full_response_content,
                metadata={"streamed": True, "final_event": last_event_data}
            )
            logger.debug(f"[SSE] Saved streamed conversation for session '{session_id}'.")
        elif not full_response_content:
            logger.warning(f"[SSE] No response content generated to save for session '{session_id}'. Last event: {last_event_data}")

    except HTTPException: # Let HTTPExceptions propagate if raised by agent or dependencies
        error_payload = {"type": "error", "detail": "An internal server error occurred during streaming.", "critical": True}
        yield f"data: {json.dumps(error_payload)}\n\n"
        raise # Re-raise to be handled by FastAPI error handlers
    except Exception as e:
        error_msg = str(e)
        logger.error(f"[SSE] Error during streaming chat for session '{session_id}': {error_msg}", exc_info=True)
        error_type = "error"
        detail_msg = f"An unexpected error occurred during streaming: {error_msg}"
        critical_error = True # Assume unexpected errors are critical for client handling

        if any(keyword in error_msg.lower() for keyword in ["rate limit", "ratelimit", "quota exceeded", "429"]):
            detail_msg = "The AI model is currently experiencing high demand (rate limit). Please try again shortly."
            # For SSE, we send an error event; client should handle this.
        
        error_payload = {"type": error_type, "detail": detail_msg, "critical": critical_error}
        yield f"data: {json.dumps(error_payload)}\n\n"
    finally:
        logger.debug(f"[SSE] Event generator finished for session '{session_id}'.")

@router.post("/chat-stream", tags=["Chat"], summary="Send a message for a streaming response (SSE)")
async def chat_stream_post_endpoint(
    payload: ChatMessageInput = Body(...),
    agent: StreamingAgent = Depends(get_current_active_agent)
):
    """
    Handles chat messages and provides a streaming response using Server-Sent Events (SSE).
    Conversation history is automatically prepended.
    """
    logger.info(f"[/chat-stream POST] Received message for session '{payload.session_id}': '{payload.message[:50]}...'")
    
    history_context = await memory_manager.get_formatted_conversation_history(
        session_id=payload.session_id, 
        limit=settings.MAX_HISTORY_MESSAGES
    )
    
    full_prompt_with_history = payload.message.strip()
    if history_context:
        full_prompt_with_history = f"{history_context}\n\nUser: {payload.message.strip()}"
        logger.debug(f"[/chat-stream POST] Using context of {len(history_context.splitlines())} lines for session '{payload.session_id}'.")

    return StreamingResponse(
        sse_event_generator(full_prompt_with_history, payload.session_id, agent), 
        media_type="text/event-stream"
    )

@router.get("/chat-stream", tags=["Chat"], summary="Send a message for a streaming response (SSE) via GET")
async def chat_stream_get_endpoint(
    message: str = Query(..., description="The user's message.", min_length=1),
    session_id: Optional[str] = Query("default", description="Identifier for the conversation session."),
    agent: StreamingAgent = Depends(get_current_active_agent)
):
    """
    GET version of the chat-stream endpoint. Convenient for browser testing.
    Conversation history is automatically prepended.
    """
    logger.info(f"[/chat-stream GET] Received message for session '{session_id}': '{message[:50]}...'")

    history_context = await memory_manager.get_formatted_conversation_history(
        session_id=session_id, 
        limit=settings.MAX_HISTORY_MESSAGES
    )
    
    full_prompt_with_history = message.strip()
    if history_context:
        full_prompt_with_history = f"{history_context}\n\nUser: {message.strip()}"
        logger.debug(f"[/chat-stream GET] Using context of {len(history_context.splitlines())} lines for session '{session_id}'.")

    return StreamingResponse(
        sse_event_generator(full_prompt_with_history, session_id, agent), 
        media_type="text/event-stream"
    )

@router.get("/health", tags=["General"], summary="Perform a health check of the API and Agent")
async def health_check() -> Dict[str, Any]:
    """
    Provides a health check of the API, including agent status and configuration.
    """
    logger.debug("[/health] Health check requested.")
    agent_status = "unknown"
    agent_tools = []
    try:
        current_agent = get_agent_instance() # Checks if agent is initialized
        agent_status = "healthy"
        if current_agent and hasattr(current_agent, 'tools'):
            agent_tools = [tool.name if hasattr(tool, 'name') else tool.__class__.__name__ for tool in current_agent.tools]
    except RuntimeError:
        agent_status = "unavailable (not initialized)"
    except Exception as e:
        agent_status = f"error ({str(e)})"
        logger.error(f"[/health] Error during agent status check: {e}", exc_info=True)

    return {
        "api_status": "healthy",
        "agent_status": agent_status,
        "agent_tools_loaded": agent_tools,
        "google_api_key_configured": settings.is_google_api_key_valid,
        "mem0_api_key_configured": settings.is_mem0_api_key_valid,
        "web_search_enabled": settings.ENABLE_WEB_SEARCH,
        "max_history_messages": settings.MAX_HISTORY_MESSAGES,
        "environment": settings.ENVIRONMENT,
        "version": "2.0.0" # Should match app version
    }

@router.get("/integrations", tags=["General"], summary="List available agent integrations/tools")
async def list_integrations(
    agent: StreamingAgent = Depends(get_current_active_agent)
) -> Dict[str, List[Dict[str, str]]]:
    """
    Lists all tools currently loaded and available to the main agent.
    """
    logger.debug("[/integrations] Integrations list requested.")
    integrations = []
    if agent and hasattr(agent, "tools") and agent.tools:
        for tool in agent.tools:
            integrations.append({
                "name": tool.name if hasattr(tool, 'name') else tool.__class__.__name__,
                "description": tool.description if hasattr(tool, 'description') else "N/A",
                "status": "enabled" # Assuming all loaded tools are enabled
            })
    return {"integrations": integrations}

# Add more routes here as needed, e.g., for specific tool interactions, memory management, etc. 