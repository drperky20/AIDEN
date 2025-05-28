"""
Example tools for AIDEN V2

This module demonstrates how to create custom tools for AIDEN using Agno.
"""
import logging
from datetime import datetime
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.reasoning import ReasoningTools

logger = logging.getLogger(__name__)

def get_tools():
    """
    Return a list of tool instances to be used by the agent.
    
    This function is called by the tool_loader.py module to discover tools
    in this module.
    
    Returns:
        list: A list of tool instances
    """
    logger.info("Loading example tools...")
    
    # Create a DuckDuckGoTools instance with custom configuration
    search_tool = DuckDuckGoTools(
        search=True,  # Enable web search
        news=True,    # Enable news search
        add_instructions=True  # Add usage instructions to the tool description
    )
    
    # Create a ReasoningTools instance for step-by-step reasoning
    reasoning_tool = ReasoningTools(
        add_instructions=True  # Add usage instructions to the tool description
    )
    
    # Return all tools as a list
    return [
        search_tool,
        reasoning_tool,
    ]

# You can test the tools here if you run this file directly
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    tools = get_tools()
    logger.info(f"Loaded {len(tools)} example tools:")
    for i, tool in enumerate(tools):
        logger.info(f"  {i+1}. {tool.__class__.__name__}") 