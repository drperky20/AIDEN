"""
FastAPI backend for AIDEN Agent Platform
Features:
- Long-term memory using SQLite database
- Server-Sent Events (SSE) for streaming tool activities
- Tool usage and activity visualization
- Web search capabilities via Agno framework
"""
from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import logging
from typing import Optional, Dict, Any, List
from config import settings
from agent import create_agent_with_fallback
import asyncio
import aiosqlite
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_FILE = "conversation_history.db"
MAX_HISTORY_MESSAGES = 5  # Number of past messages to include in context

async def init_db():
    """Initialize the SQLite database and create tables if they don't exist."""
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_message TEXT NOT NULL,
                agent_response TEXT NOT NULL
            )
        """)
        await db.commit()
    logger.info(f"📚 Database '{DB_FILE}' initialized.")

async def add_conversation_to_db(user_message: str, agent_response: str):
    """Add a new conversation to the database."""
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "INSERT INTO conversations (user_message, agent_response, timestamp) VALUES (?, ?, ?)",
            (user_message, agent_response, datetime.now())
        )
        await db.commit()
    logger.info("📝 Conversation saved to database.")

async def get_conversation_history(limit: int = MAX_HISTORY_MESSAGES) -> str:
    """Retrieve the last N conversation turns as a formatted string."""
    history_parts = []
    try:
        async with aiosqlite.connect(DB_FILE) as db:
            async with db.execute(
                "SELECT user_message, agent_response FROM conversations ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            ) as cursor:
                rows = await cursor.fetchall()
                for row in reversed(rows):  # Chronological order for prompt
                    history_parts.append(f"User: {row[0]}")
                    history_parts.append(f"Agent: {row[1]}")
        logger.info(f"Retrieved {len(rows)} messages from history.")
        return "\\n".join(history_parts)
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {e}")
        return ""

# Initialize FastAPI app
app = FastAPI(
    title="Agno Gemini Agent API",
    description="High-performance API backend for Agno Gemini Agent with web search capabilities",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if settings.is_production else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Global agent instance
agent: Optional[object] = None

@app.on_event("startup")
async def startup_event():
    """Initialize the agent and database on application startup"""
    global agent
    
    logger.info("🚀 Starting Agno Gemini Agent API...")
    await init_db() # Initialize database
    
    if not settings.is_api_key_valid:
        logger.warning("⚠️  GOOGLE_API_KEY not set or invalid. Please configure it to use the agent.")
        return
    
    logger.info("🤖 Initializing Agno Gemini Agent...")
    agent = create_agent_with_fallback()
    
    if agent:
        logger.info("✅ Agent initialized successfully!")
    else:
        logger.error("❌ Failed to initialize agent")

@app.post("/chat")
async def chat(message: str = Form(...)) -> Dict[str, Any]:
    """
    Handle chat messages with optimized error handling and conversation history
    
    Args:
        message: The user's message
        
    Returns:
        JSON response with either success response or error
    """
    global agent # Ensure using global agent

    if not agent:
        raise HTTPException(
            status_code=503,
            detail="Agent not initialized. Please check your GOOGLE_API_KEY configuration."
        )
    
    if not message or not message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )
    
    try:
        logger.info(f"Processing message: {message[:50]}...")
        
        history_context = await get_conversation_history()
        
        full_prompt = message.strip()
        if history_context:
            full_prompt = f"{history_context}\\n\\nUser: {message.strip()}"
            logger.info(f"Using context of {len(history_context.splitlines())} lines for the agent.")

        response_obj = agent.run(full_prompt) # Agent receives message with history
        agent_response_content = response_obj.content
        
        await add_conversation_to_db(message.strip(), agent_response_content)
        
        return {
            "response": response_obj.content,
            "success": True,
            "message_length": len(response_obj.content)
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.warning(f"Error processing message: {error_msg}")
        
        # Handle rate limiting gracefully
        if any(keyword in error_msg.lower() for keyword in ["403", "ratelimit", "rate limit", "too many requests"]):
            return {
                "response": "I'm experiencing some rate limiting with web search right now. Let me answer based on my knowledge instead!\n\nPlease feel free to ask your question again, and I'll do my best to help without searching the web.",
                "success": True,
                "rate_limited": True
            }
        
        # Handle other errors
        logger.error(f"Unexpected error: {error_msg}")
        return {
            "error": f"Error processing message: {error_msg}",
            "success": False
        }

# SSE Event Generator
async def event_generator(prompt: str, agent_instance: Any):
    """
    Yields events from the agent's stream_run method.
    Requires agent_instance to have an `async def stream_run(self, prompt: str)` method.
    """
    if not agent_instance:
        yield "data: " + json.dumps({"type": "error", "detail": "Agent not initialized"}) + "\\n\\n"
        return

    try:
        # Placeholder: agent.stream_run needs to be an async generator in your agent.py
        # It should yield dicts like:
        # {"type": "tool_start", "name": "web_search", "input": "query"}
        # {"type": "llm_chunk", "content": "partial response"}
        # {"type": "final_response", "content": "full response"}
        # {"type": "error", "detail": "error message"}
        
        # For now, let's simulate some events if stream_run is not available or for testing
        if hasattr(agent_instance, 'stream_run') and callable(agent_instance.stream_run):
            full_response_content = ""
            user_message_for_db = prompt # Store original prompt for DB

            async for event_data in agent_instance.stream_run(prompt):
                yield f"data: {json.dumps(event_data)}\\n\\n"
                await asyncio.sleep(0.01) # Ensure events are sent
                # Accumulate final response if events provide chunks
                if event_data.get("type") == "llm_chunk" and "content" in event_data:
                    full_response_content += event_data["content"]
                elif event_data.get("type") == "final_response" and "content" in event_data:
                    full_response_content = event_data["content"] # Overwrite if final_response is total

            # After stream, if we have accumulated a final response, save it.
            # This assumes stream_run will provide enough info to reconstruct the final agent response.
            # A more robust way is if stream_run itself handles saving or returns final content.
            if full_response_content:
                 # Check if the last event was an error, if so, maybe don't save or save error state
                if not (event_data and event_data.get("type") == "error"):
                    await add_conversation_to_db(user_message_for_db, full_response_content)
            else:
                logger.warning("No full response content was accumulated from the stream to save to DB.")

        else:
            logger.warning("Agent does not have a 'stream_run' method. SSE endpoint will not stream agent activity.")
            yield "data: " + json.dumps({"type": "info", "detail": "Agent streaming not implemented or 'stream_run' method missing."}) + "\\n\\n"
            # Fallback to regular run for a single response if stream_run is not available
            response_obj = agent_instance.run(prompt)
            agent_response_content = response_obj.content
            await add_conversation_to_db(prompt, agent_response_content)
            yield "data: " + json.dumps({"type": "final_response", "content": agent_response_content}) + "\\n\\n"
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error during streaming chat: {error_msg}")
        error_payload = {"type": "error", "detail": f"Error processing message: {error_msg}"}
        if any(keyword in error_msg.lower() for keyword in ["403", "ratelimit", "rate limit", "too many requests"]):
            error_payload = {
                "type": "error",
                "detail": "Rate limit likely hit during stream.",
                "rate_limited": True
            }
        yield f"data: {json.dumps(error_payload)}\\n\\n"


@app.post("/chat-stream")
async def chat_stream_endpoint(message: str = Form(...)):
    """
    Handles chat messages with a streaming response (SSE).
    Requires the agent to have an `async def stream_run(self, prompt: str)` method
    that yields events (e.g., tool usage, text chunks).
    Conversation history is automatically prepended to the message.
    """
    global agent # Use the global agent instance

    if not message or not message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    if not agent:
        async def immediate_error_gen():
            yield "data: " + json.dumps({
                "type": "error",
                "detail": "Agent not initialized. Please check GOOGLE_API_KEY."
            }) + "\\n\\n"
        return StreamingResponse(immediate_error_gen(), media_type="text/event-stream")

    history_context = await get_conversation_history()
    full_prompt_with_history = message.strip()
    if history_context:
        full_prompt_with_history = f"{history_context}\\n\\nUser: {message.strip()}"
        logger.info(f"Streaming with context of {len(history_context.splitlines())} lines.")
    
    return StreamingResponse(event_generator(full_prompt_with_history, agent), media_type="text/event-stream")

@app.get("/chat-stream")
async def chat_stream_get_endpoint(message: str):
    """
    GET version of the chat-stream endpoint that accepts the message as a query parameter.
    This endpoint works the same as the POST version but is more convenient for testing.
    """
    global agent # Use the global agent instance

    if not message or not message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    if not agent:
        async def immediate_error_gen():
            yield "data: " + json.dumps({
                "type": "error",
                "detail": "Agent not initialized. Please check GOOGLE_API_KEY."
            }) + "\\n\\n"
        return StreamingResponse(immediate_error_gen(), media_type="text/event-stream")

    history_context = await get_conversation_history()
    full_prompt_with_history = message.strip()
    if history_context:
        full_prompt_with_history = f"{history_context}\\n\\nUser: {message.strip()}"
        logger.info(f"Streaming with context of {len(history_context.splitlines())} lines.")
    
    return StreamingResponse(event_generator(full_prompt_with_history, agent), media_type="text/event-stream")

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Comprehensive health check endpoint
    
    Returns:
        System health status and configuration info
    """
    return {
        "status": "healthy" if agent else "degraded",
        "agent_initialized": agent is not None,
        "api_key_configured": settings.is_api_key_valid,
        "web_search_enabled": settings.ENABLE_WEB_SEARCH,
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0"
    }

@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint with API information"""
    return {
        "message": "Agno Gemini Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/integrations")
async def list_integrations() -> Dict[str, List[Dict[str, str]]]:
    """
    List all available integrations/tools loaded in the agent.
    Returns a list of tool names and their status.
    """
    global agent
    if not agent or not hasattr(agent, "tools"):
        return {"integrations": []}
    integrations = []
    for tool in agent.tools:
        tool_name = tool.__class__.__name__
        # For now, all loaded tools are "enabled"
        integrations.append({
            "name": tool_name,
            "status": "enabled"
        })
    return {"integrations": integrations}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=settings.API_HOST, 
        port=settings.API_PORT,
        reload=settings.API_RELOAD
    ) 