"""
AIDEN V2 FastAPI Application Main

Initializes the FastAPI app, CORS, logging, and handles startup/shutdown events
such as initializing the database and the agent.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.core.memory import memory_manager # Updated import
from backend.agent.agent_factory import initialize_global_agent, get_agent_instance # Updated import
from .routes import router as api_router # Will create routes.py next

# Configure logging basicConfig should be called once, typically at the application entry point.
# If other modules also call it, it might lead to unexpected behavior or suppress logs.
# We can refine this later if needed, e.g. using a common logging setup utility.
logging.basicConfig(level=logging.INFO if settings.ENVIRONMENT == "production" else logging.DEBUG)
logger = logging.getLogger(__name__) # Main application logger

app = FastAPI(
    title="AIDEN V2 Agent API",
    description="Next-generation AI Personal Assistant API leveraging Agno and Gemini.",
    version="2.0.0",
    debug=not settings.is_production,
    # Add other FastAPI configurations like docs_url, redoc_url if needed
)

# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], # Expanded methods
    allow_headers=["*"] # Allow all headers
)

@app.on_event("startup")
async def startup_event_handler():
    """Handles application startup events."""
    logger.info("🚀 AIDEN V2 API is starting up...")
    
    # 1. Initialize Database
    logger.info("Initializing database...")
    try:
        await memory_manager.initialize_database()
        logger.info("✅ Database initialized successfully.")
    except Exception as e:
        logger.critical(f"❌ CRITICAL: Failed to initialize database: {e}", exc_info=True)
        # Depending on severity, you might want to prevent app startup
        # For now, we log critical and continue, agent might fail later or work without DB history.

    # 2. Initialize Agent
    # Ensure API key is valid before attempting to initialize agent that might use it.
    if not settings.is_google_api_key_valid:
        logger.critical("❌ CRITICAL: GOOGLE_API_KEY is not set or invalid. Agent will not be initialized.")
        logger.critical("Please set your GOOGLE_API_KEY in the .env file.")
        # You could raise an exception here to halt startup if the agent is critical
        # For now, the agent initialization will likely fail or create a very basic agent.
    
    logger.info("Initializing AIDEN Agent...")
    try:
        # Initialize the global agent instance (default to "main" type)
        initialize_global_agent(agent_type="main") 
        # Attempt to get the instance to confirm it was set
        _ = get_agent_instance() # This will raise RuntimeError if current_agent is None
        logger.info("✅ AIDEN Agent initialized successfully.")
    except ValueError as ve: # Specific error from create_gemini_model if API key is bad
        logger.critical(f"❌ CRITICAL: Failed to initialize agent due to configuration: {ve}", exc_info=True)
    except RuntimeError as re:
        logger.critical(f"❌ CRITICAL: Failed to initialize agent: {re}", exc_info=True)
    except Exception as e:
        logger.critical(f"❌ CRITICAL: An unexpected error occurred during agent initialization: {e}", exc_info=True)
    
    logger.info("🎉 AIDEN V2 API startup sequence complete.")

@app.on_event("shutdown")
async def shutdown_event_handler():
    """Handles application shutdown events."""
    logger.info("🛌 AIDEN V2 API is shutting down...")
    # Add any cleanup logic here (e.g., closing database connections if not handled by context managers)
    logger.info("👋 Goodbye!")

# Include API routes
app.include_router(api_router)

# Root endpoint for basic API info
@app.get("/", tags=["General"], summary="API Root Endpoint")
async def root():
    """Provides basic information about the API."""
    return {
        "message": "Welcome to the AIDEN V2 Agent API!",
        "version": app.version,
        "docs_url": app.docs_url,
        "redoc_url": app.redoc_url,
        "health_url": "/health" # Assuming /health will be in api_router
    }

# To run this app (example, if you were to run it directly, though uvicorn from command line is standard):
# if __name__ == "__main__":
#     import uvicorn
#     logger.info(f"Starting Uvicorn development server on http://{settings.API_HOST}:{settings.API_PORT}")
#     uvicorn.run(
#         "backend.api.main:app", 
#         host=settings.API_HOST, 
#         port=settings.API_PORT, 
#         reload=settings.API_RELOAD,
#         # log_level can be set here too, but basicConfig is often preferred for global setup
#         log_level= "debug" if not settings.is_production else "info"
#     ) 