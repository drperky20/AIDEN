"""
AIDEN V2 Agent Package

This package contains the core agent logic, including the StreamingAgent, 
tool loading, agent creation factories, and future specialized agents/teams.
"""

from .base_agent import StreamingAgent, create_gemini_model
from .tool_loader import load_all_tools
from .agent_factory import (
    create_main_agent,
    create_simple_agent,
    get_agent_instance,
    initialize_global_agent,
    current_agent # Export for direct access if needed, though get_agent_instance is preferred
)

__all__ = [
    "StreamingAgent",
    "create_gemini_model",
    "load_all_tools",
    "create_main_agent",
    "create_simple_agent",
    "get_agent_instance",
    "initialize_global_agent",
    "current_agent"
] 