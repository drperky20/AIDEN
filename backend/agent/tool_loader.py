"""
Dynamic Tool Loader for AIDEN V2 Agents

This module is responsible for loading tools for the AIDEN V2 agent.
It provides both pre-configured tools from Agno and custom tools from the backend/tools directory.
"""
import importlib
import pkgutil
import logging
from pathlib import Path
from typing import List, Any

# Import specific Agno tools that we want to use
from agno.tools.reasoning import ReasoningTools
# Add other Agno tool imports as needed, for example:
# from agno.tools.duckduckgo import DuckDuckGoTools
# from agno.tools.yfinance import YFinanceTools

logger = logging.getLogger(__name__)

# Path to the custom tools directory
TOOLS_DIR = Path(__file__).parent.parent / "tools"
TOOLS_PACKAGE_PATH = "backend.tools"  # Python import path for tools

def load_all_tools() -> List[Any]:
    """
    Load all tools for the AIDEN V2 agent.
    
    This includes:
    1. Pre-configured Agno tools
    2. Custom tools from the backend/tools directory
    
    Returns:
        List[Any]: List of tool instances ready to be used by the agent
    """
    tool_instances = []
    
    # Add pre-configured Agno tools
    tool_instances.append(ReasoningTools(add_instructions=True))
    # Add other Agno tools as needed, for example:
    # tool_instances.append(DuckDuckGoTools())
    # tool_instances.append(YFinanceTools())
    
    # Try to load custom tools from the backend/tools directory
    custom_tools = load_custom_tools()
    if custom_tools:
        tool_instances.extend(custom_tools)
        
    logger.info(f"Loaded {len(tool_instances)} tools in total")
    return tool_instances

def load_custom_tools() -> List[Any]:
    """
    Dynamically import custom tool classes from the backend/tools directory.
    
    Each tool file should contain a class with a get_tools() function that returns
    a list of tool instances.
    
    Returns:
        List[Any]: List of custom tool instances
    """
    custom_tools = []
    
    if not TOOLS_DIR.exists() or not TOOLS_DIR.is_dir():
        logger.warning(f"Custom tools directory not found or is not a directory: {TOOLS_DIR}")
        return custom_tools

    logger.info(f"Looking for custom tools in: {TOOLS_DIR}")

    # Create __init__.py if it doesn't exist to make the directory a proper package
    init_file = TOOLS_DIR / "__init__.py"
    if not init_file.exists():
        init_file.touch()
        logger.info(f"Created {init_file} to make the tools directory a proper package")

    # Iterate through modules in the tools directory
    for _, module_name, _ in pkgutil.iter_modules([str(TOOLS_DIR)]):
        if module_name.startswith("__"):  # Skip __init__.py etc.
            continue
            
        try:
            module_path = f"{TOOLS_PACKAGE_PATH}.{module_name}"
            module = importlib.import_module(module_path)
            logger.debug(f"Successfully imported module: {module_path}")
            
            # Look for a get_tools function in the module
            if hasattr(module, 'get_tools') and callable(module.get_tools):
                tools = module.get_tools()
                if isinstance(tools, list):
                    custom_tools.extend(tools)
                    logger.info(f"Added {len(tools)} tools from {module_path}")
                else:
                    logger.warning(f"get_tools() in {module_path} did not return a list")
            else:
                logger.debug(f"No get_tools() function found in {module_path}")
                
        except ImportError as e:
            logger.error(f"Failed to import module {module_name}: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Error loading tools from {module_name}: {e}", exc_info=True)
    
    logger.info(f"Loaded {len(custom_tools)} custom tools")
    return custom_tools

# Example of how a custom tool module should be structured:
"""
# Example file: backend/tools/my_custom_tools.py

from agno.tools.duckduckgo import DuckDuckGoTools
# Or other imports as needed

def get_tools():
    # Return a list of tool instances
    return [
        DuckDuckGoTools(search=True, news=False),
        # Other tool instances...
    ]
"""

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger.info("Testing tool loader...")
    
    tools = load_all_tools()
    logger.info(f"Loaded {len(tools)} tools in total")
    for i, tool in enumerate(tools):
        logger.info(f"Tool {i+1}: {tool.__class__.__name__}") 