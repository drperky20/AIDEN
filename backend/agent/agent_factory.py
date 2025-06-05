"""
Agent Factory for AIDEN V2

Provides functions to create different configurations of AIDEN agents.
"""
import logging
from typing import Optional, List

from agno.tools.duckduckgo import DuckDuckGoTools # Standard web search tool

from backend.config import settings
from backend.agent.base_agent import StreamingAgent, create_gemini_model
from backend.agent.tool_loader import load_all_tools # Updated import
from backend.models.openrouter import OpenRouterModel
# Import other specialized agents or teams here as they are developed
# from backend.agent.specialized_agents import FileAgent, CodeAgent # etc.
# from backend.agent.agent_teams import create_main_team

logger = logging.getLogger(__name__)

DEFAULT_INSTRUCTIONS = [
    "You are AIDEN, a highly capable AI personal assistant powered by Llama 4 Maverick (via OpenRouter).",
    "You leverage the latest multimodal AI capabilities to assist users with a wide range of tasks.",
    "Be proactive, thoughtful, and clear in your responses with minimal latency.",
    "If you use tools, briefly mention what you're doing (e.g., 'Searching the web for...' or 'Accessing files to...').",
    "Provide answers in Markdown format when it enhances readability (e.g., for lists, code blocks).",
    "If you encounter an error with a tool, acknowledge it and try to answer based on your existing knowledge or suggest an alternative.",
    "Maintain a conversational and helpful tone, optimized for both text and voice interactions."
]

def create_model():
    """
    Create the best available model based on configuration.
    Prioritizes OpenRouter with Llama 4 Maverick, falls back to Gemini.
    """
    logger.info("Selecting optimal model based on configuration...")
    
    model_type = settings.preferred_model_type
    
    if model_type == "openrouter":
        try:
            logger.info(f"Creating OpenRouter model: {settings.OPENROUTER_MODEL_ID}")
            model = OpenRouterModel(
                id=settings.OPENROUTER_MODEL_ID,
                api_key=settings.OPENROUTER_API_KEY,
                temperature=0.7,  # Balanced creativity and consistency
                max_tokens=4000,  # Reasonable response length
            )
            logger.info("✅ OpenRouter model created successfully")
            return model
        except Exception as e:
            logger.error(f"Failed to create OpenRouter model: {e}")
            logger.info("Falling back to Gemini model...")
    
    # Fallback to Gemini
    if model_type == "gemini" or model_type == "none":
        try:
            if settings.is_google_api_key_valid:
                logger.info("Creating Gemini fallback model")
                model = create_gemini_model()
                logger.info("✅ Gemini model created successfully")
                return model
            else:
                logger.error("No valid API keys available for any model")
                raise ValueError("No valid model configuration found. Please set OPENROUTER_API_KEY or GOOGLE_API_KEY")
        except Exception as e:
            logger.error(f"Failed to create Gemini model: {e}")
            raise
    
    raise ValueError("Unable to create any model")

def create_main_agent(instructions: Optional[List[str]] = None) -> StreamingAgent:
    """
    Creates the main AIDEN agent with all tools and the best available model.
    This will be the primary agent used for most interactions.
    """
    logger.info("Creating main AIDEN agent with optimized model selection...")
    try:
        model = create_model()
        
        # Load all tools (both pre-configured and custom)
        tools = load_all_tools()
        
        # Always include DuckDuckGoTools if web search is enabled and not already included
        if settings.ENABLE_WEB_SEARCH:
            if not any(isinstance(tool, DuckDuckGoTools) for tool in tools):
                tools.append(DuckDuckGoTools())
                logger.info("Added DuckDuckGoTools for web search.")
            else:
                logger.info("DuckDuckGoTools already present in tools.")
        
        # TODO: In the future, specialized agents (FileAgent, CodeAgent) might be composed here
        # or this agent might become part of a larger Agno Team.

        final_instructions = instructions if instructions else DEFAULT_INSTRUCTIONS

        agent = StreamingAgent(
            model=model,
            tools=tools,
            instructions=final_instructions,
            show_tool_calls=settings.SHOW_TOOL_CALLS,
            markdown=settings.ENABLE_MARKDOWN,
            # id="aiden_main_agent", # Optional: give the agent an ID
            # description="Main AIDEN assistant agent", # Optional description
        )
        
        model_info = f"{model.__class__.__name__}"
        if hasattr(model, 'id'):
            model_info += f" ({model.id})"
        
        logger.info(f"✅ Main AIDEN agent created successfully with {len(tools)} tools using {model_info}")
        return agent
    except Exception as e:
        logger.error(f"Failed to create main AIDEN agent: {e}", exc_info=True)
        # Fallback to a simple agent in case of catastrophic failure during main agent creation
        logger.warning("Falling back to a simple agent due to an error in main agent creation.")
        return create_simple_agent(instructions=instructions, error_context=str(e))

def create_simple_agent(instructions: Optional[List[str]] = None, error_context: Optional[str] = None) -> StreamingAgent:
    """
    Creates a basic AIDEN agent without dynamic tools or web search.
    Useful for testing, fallback, or specific simple tasks.
    """
    logger.info("Creating simple AIDEN agent...")
    if error_context:
        logger.warning(f"Simple agent is being created due to a previous error: {error_context}")

    try:
        # Try to create the best available model first
        try:
            model = create_model()
        except Exception as model_error:
            logger.error(f"Failed to create optimal model for simple agent: {model_error}")
            # Ultimate fallback to Gemini if available
            if settings.is_google_api_key_valid:
                logger.info("Using Gemini as ultimate fallback")
                model = create_gemini_model()
            else:
                raise ValueError("No working model available")
        
        simple_instructions = instructions if instructions else [
            "You are AIDEN, a helpful AI assistant (basic mode).",
            "Provide concise and accurate responses based on your training data.",
            "Tool usage is currently limited in this mode."
        ]
        if error_context:
            simple_instructions.append(f"Note: Advanced features may be temporarily unavailable due to: {error_context}")

        agent = StreamingAgent(
            model=model,
            tools=[], # No tools for the simple agent by default
            instructions=simple_instructions,
            show_tool_calls=False, # Typically false for simple agent
            markdown=settings.ENABLE_MARKDOWN,
            # id="aiden_simple_agent",
        )
        logger.info("✅ Simple AIDEN agent created successfully.")
        return agent
    except Exception as e:
        logger.critical(f"FATAL: Failed to create even the simple AIDEN agent: {e}", exc_info=True)
        # If even the simple agent fails, we might need to raise the exception
        # or return a dummy agent that only says it's offline.
        raise  # Re-raise the exception as this is critical


# Global agent instance, to be initialized by the application (e.g., FastAPI startup)
# This allows the application to decide when and how to initialize the agent.
current_agent: Optional[StreamingAgent] = None

def get_agent_instance() -> StreamingAgent:
    """
    Returns the globally managed agent instance.
    Raises an error if the agent has not been initialized.
    """
    if current_agent is None:
        logger.error("Agent instance requested before initialization.")
        raise RuntimeError("AIDEN agent has not been initialized. The application may not have started correctly.")
    return current_agent

def initialize_global_agent(agent_type: str = "main"):
    """
    Initializes the global agent instance.
    Called at application startup.
    Args:
        agent_type: "main" or "simple".
    """
    global current_agent
    logger.info(f"Initializing global AIDEN agent (type: {agent_type})...")
    
    # Log configuration info
    model_type = settings.preferred_model_type
    logger.info(f"Model preference: {model_type}")
    if model_type == "openrouter":
        logger.info(f"OpenRouter model: {settings.OPENROUTER_MODEL_ID}")
    elif model_type == "gemini":
        logger.info(f"Gemini model: {settings.GEMINI_MODEL_ID}")
    
    if agent_type == "main":
        current_agent = create_main_agent()
    elif agent_type == "simple":
        current_agent = create_simple_agent()
    else:
        logger.warning(f"Unknown agent type '{agent_type}'. Defaulting to main agent.")
        current_agent = create_main_agent()
    
    if current_agent:
        logger.info(f"✅ Global AIDEN agent (type: {agent_type}) initialized successfully.")
    else:
        # This case should ideally be handled by exceptions in create_xxx_agent
        logger.error(f"Failed to initialize global AIDEN agent (type: {agent_type}). Using a dummy fallback.")
        # Create a dummy non-functional agent or raise critical error
        # For now, let's assume create_simple_agent handles its own critical failures by raising
        # If create_main_agent falls back, it calls simple, which might raise.
        # This path implies even simple agent creation failed AND didn't raise, which is unlikely.
        pass # Or raise a specific error for the application to handle

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    
    print("--- Testing Main Agent Creation ---")
    main_agent = create_main_agent()
    if main_agent:
        print(f"Main agent created. Tools: {[t.name for t in main_agent.tools if hasattr(t, 'name')]}")
        print(f"Model: {main_agent.model.__class__.__name__}")
        # response = main_agent.run("Hello AIDEN! What can you do?")
        # print(f"Main Agent Response: {response.content if hasattr(response, 'content') else response}")
    else:
        print("Failed to create main agent.")

    print("\n--- Testing Simple Agent Creation ---")
    simple_agent = create_simple_agent()
    if simple_agent:
        print(f"Simple agent created. Tools: {simple_agent.tools}")
        print(f"Model: {simple_agent.model.__class__.__name__}")
        # response_simple = simple_agent.run("Hello AIDEN (simple mode)!")
        # print(f"Simple Agent Response: {response_simple.content if hasattr(response_simple, 'content') else response_simple}")
    else:
        print("Failed to create simple agent.")

    print("\n--- Testing Global Agent Initialization ---")
    try:
        initialize_global_agent("main")
        agent_instance = get_agent_instance()
        print(f"Global agent initialized. Type: {agent_instance.__class__.__name__}, Tools: {[t.name for t in agent_instance.tools if hasattr(t, 'name')]}")
    except Exception as e:
        print(f"Error initializing or getting global agent: {e}") 