# agents/base_agent.py
"""
Base agent class providing common functionality for all agents.

This module provides the BaseAgent abstract base class that serves as the foundation
for all agent implementations in the multi-tool research project.  It provides:

- Tool management and integration
- Memory handling for interactions
- Configuration loading and validation
- Consistent interface for agent execution

Example:
    Creating a custom agent:

    >>> from agents.base_agent import BaseAgent
    >>> from tools.web_search_tool import WebSearchTool
    >>> 
    >>> class MyCustomAgent(BaseAgent):
    ...    def __init__(self):
    ...        super().__init__("MyAgent", "Does custom research tasks")
    ...        self.add_tool(WebSearchTool())
    ...    
    ...    def execute(self, query: str, context=None):
    ...        # Implementation here
    ...        return {"response": "...", "sources": [...]}

    Using the agent:

    >>> agent = MyCustomAgent()
    >>> result = agent.execute("What is the capital of France?")
    >>> print(result["response"])

Usage Patterns:
- Always call super().init() in subclass constructors
- Add tools during initialization or dynamically as needed
- Use add_to_memory() to maintain conversation context
- Return consistent dictionary format from execute() method
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from utils.config import Config

class BaseAgent(ABC):
    """Abstract base class for all agents."""
    
    def __init__(self, name: str, description: str = ""):
        """Initialize the base agent.
        
        Args:
            name: The name of the agent
            description: A description of what the agent does
        """
        self.name = name
        self.description = description
        self.config = Config()
        self.config.validate()
        self.tools: List[Any] = []
        self.memory: List[Dict[str, Any]] = []
    
    def add_tool(self, tool: Any) -> None:
        """Add a tool to the agent's toolkit.
        
        Args:
            tool: The tool to add
        """
        self.tools.append(tool)
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names."""
        return [tool.name for tool in self.tools if hasattr(tool, 'name')]
    
    @abstractmethod
    def execute(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute the agent with a given query.
        
        Args:
            query: The input query to process
            context: Optional context for the query
            
        Returns:
            Dictionary containing the agent's response
        """
        pass
    
    def add_to_memory(self, interaction: Dict[str, Any]) -> None:
        """Add an interaction to the agent's memory.
        
        Args:
            interaction: Dictionary containing interaction details
        """
        self.memory.append(interaction)
        # Keep memory within size limits
        if len(self.memory) > self.config.MEMORY_SIZE:
            self.memory = self.memory[-self.config.MEMORY_SIZE:]