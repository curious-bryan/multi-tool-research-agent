# tests/test_base_agent.py
"""
Comprehensive test suite for the BaseAgent class.

Tests cover:
- Abstract class enforcement
- Tool management
- Memory operations
- Configuration handling
- Error conditions
- Integration scenarios
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from agents.base_agent import BaseAgent
from tools.calculator_tool import CalculatorTool
from utils.config import Config


class ConcreteAgent(BaseAgent):
    """Concrete implementation of BaseAgent for testing."""
    
    def execute(self, query: str, context=None):
        """Simple implementation for testing."""
        return {
            "response": f"Processed: {query}",
            "context": context,
            "tools_used": [tool.name for tool in self.tools]
        }


class TestBaseAgentInstantiation:
    """Test agent creation and initialization."""
    
    def test_cannot_instantiate_abstract_base_agent(self):
        """BaseAgent is abstract and cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseAgent("test", "description")
    
    def test_concrete_agent_instantiation(self):
        """Concrete agent can be instantiated with required parameters."""
        agent = ConcreteAgent("TestAgent", "Test description")
        
        assert agent.name == "TestAgent"
        assert agent.description == "Test description"
        assert isinstance(agent.config, Config)
        assert agent.tools == []
        assert agent.memory == []
    
    def test_agent_with_minimal_parameters(self):
        """Agent can be created with just a name."""
        agent = ConcreteAgent("MinimalAgent")
        
        assert agent.name == "MinimalAgent"
        assert agent.description == ""
    
    @patch('utils.config.Config.validate')
    def test_config_validation_called_on_init(self, mock_validate):
        """Config validation is called during agent initialization."""
        ConcreteAgent("TestAgent")
        mock_validate.assert_called_once()


class TestToolManagement:
    """Test tool addition and management functionality."""
    
    def test_add_single_tool(self):
        """Agent can add a single tool."""
        agent = ConcreteAgent("TestAgent")
        calculator = CalculatorTool()
        
        agent.add_tool(calculator)
        
        assert len(agent.tools) == 1
        assert agent.tools[0] == calculator
    
    def test_add_multiple_tools(self):
        """Agent can add multiple tools."""
        agent = ConcreteAgent("TestAgent")
        calc1 = CalculatorTool()
        calc2 = CalculatorTool()
        
        agent.add_tool(calc1)
        agent.add_tool(calc2)
        
        assert len(agent.tools) == 2
        assert calc1 in agent.tools
        assert calc2 in agent.tools
    
    def test_get_available_tools_with_named_tools(self):
        """get_available_tools returns tool names for tools with name attribute."""
        agent = ConcreteAgent("TestAgent")
        calculator = CalculatorTool()  # Has name attribute
        
        agent.add_tool(calculator)
        tools = agent.get_available_tools()
        
        assert tools == ["calculator"]
    
    def test_get_available_tools_without_name_attribute(self):
        """Tools without name attribute are excluded from available tools list."""
        agent = ConcreteAgent("TestAgent")
        mock_tool = Mock()
        del mock_tool.name  # Remove name attribute
        
        agent.add_tool(mock_tool)
        tools = agent.get_available_tools()
        
        assert tools == []
    
    def test_get_available_tools_mixed_tools(self):
        """Mixed tools (with and without name) handled correctly."""
        agent = ConcreteAgent("TestAgent")
        calculator = CalculatorTool()
        mock_tool = Mock()
        del mock_tool.name
        
        agent.add_tool(calculator)
        agent.add_tool(mock_tool)
        tools = agent.get_available_tools()
        
        assert tools == ["calculator"]


class TestMemoryManagement:
    """Test conversation memory functionality."""
    
    def test_add_interaction_to_memory(self):
        """Agent can store interactions in memory."""
        agent = ConcreteAgent("TestAgent")
        interaction = {"query": "test", "response": "result"}
        
        agent.add_to_memory(interaction)
        
        assert len(agent.memory) == 1
        assert agent.memory[0] == interaction
    
    def test_add_multiple_interactions(self):
        """Agent can store multiple interactions."""
        agent = ConcreteAgent("TestAgent")
        interactions = [
            {"query": "test1", "response": "result1"},
            {"query": "test2", "response": "result2"}
        ]
        
        for interaction in interactions:
            agent.add_to_memory(interaction)
        
        assert len(agent.memory) == 2
        assert agent.memory == interactions
    
    @patch.object(Config, 'MEMORY_SIZE', 3)
    def test_memory_size_limit_enforcement(self):
        """
        Test that agent memory is properly truncated when exceeding configured size.
        
        Given: An agent with memory size limit of 3
        When: 5 interactions are added to memory
        Then: Only the last 3 interactions should be retained
        """
        agent = ConcreteAgent("TestAgent")
        
        # Add more interactions than memory size limit
        for i in range(5):
            agent.add_to_memory({"query": f"test{i}", "response": f"result{i}"})
        
        # Should only keep the last 3 interactions
        assert len(agent.memory) == 3
        assert agent.memory[0]["query"] == "test2"  # First kept interaction
        assert agent.memory[-1]["query"] == "test4"  # Last interaction
    
    def test_memory_with_complex_interaction_data(self):
        """Agent can store complex interaction data structures."""
        agent = ConcreteAgent("TestAgent")
        complex_interaction = {
            "query": "complex query",
            "response": "detailed response",
            "metadata": {
                "tools_used": ["calculator", "web_search"],
                "execution_time": 1.5,
                "tokens_used": 150
            },
            "context": {"user_id": "123", "session_id": "abc"}
        }
        
        agent.add_to_memory(complex_interaction)
        
        assert agent.memory[0] == complex_interaction
        assert agent.memory[0]["metadata"]["tools_used"] == ["calculator", "web_search"]


class TestExecuteMethod:
    """Test the abstract execute method implementation."""
    
    def test_execute_basic_functionality(self):
        """Concrete execute implementation works as expected."""
        agent = ConcreteAgent("TestAgent")
        result = agent.execute("test query")
        
        assert result["response"] == "Processed: test query"
        assert result["context"] is None
        assert result["tools_used"] == []
    
    def test_execute_with_context(self):
        """Execute method handles context parameter."""
        agent = ConcreteAgent("TestAgent")
        context = {"user": "testuser", "session": "123"}
        
        result = agent.execute("test query", context)
        
        assert result["context"] == context
    
    def test_execute_reflects_available_tools(self):
        """Execute method reflects tools added to agent."""
        agent = ConcreteAgent("TestAgent")
        calculator = CalculatorTool()
        agent.add_tool(calculator)
        
        result = agent.execute("test query")
        
        assert "calculator" in result["tools_used"]


class TestConfigurationIntegration:
    """Test configuration system integration."""
    
    @patch('utils.config.Config.validate', side_effect=ValueError("Invalid config"))
    def test_config_validation_failure(self, mock_validate):
        """
        Test agent initialization fails when config validation fails.
        
        Mocks config validation to simulate failure scenarios without
        requiring actual invalid configuration files.
        """
        with pytest.raises(ValueError, match="Invalid config"):
            ConcreteAgent("TestAgent")
    
    @patch.object(Config, 'MEMORY_SIZE', 10)
    def test_config_memory_size_usage(self):
        """Agent uses configured memory size from Config."""
        agent = ConcreteAgent("TestAgent")
        
        # Add interactions up to but not exceeding memory size
        for i in range(10):
            agent.add_to_memory({"query": f"test{i}"})
        
        assert len(agent.memory) == 10
        
        # Adding one more should trigger truncation
        agent.add_to_memory({"query": "test10"})
        assert len(agent.memory) == 10  # Still at limit
        assert agent.memory[0]["query"] == "test1"  # First item removed


class TestErrorHandling:
    """Test error conditions and edge cases."""
    
    def test_add_none_tool(self):
        """Adding None as a tool doesn't break the agent."""
        agent = ConcreteAgent("TestAgent")
        agent.add_tool(None)
        
        assert len(agent.tools) == 1
        assert agent.tools[0] is None
    
    def test_get_available_tools_with_none_tool(self):
        """get_available_tools handles None tools gracefully."""
        agent = ConcreteAgent("TestAgent")
        agent.add_tool(None)
        
        # Should not raise an exception
        tools = agent.get_available_tools()
        assert tools == []
    
    def test_add_to_memory_with_none(self):
        """Adding None to memory is handled."""
        agent = ConcreteAgent("TestAgent")
        agent.add_to_memory(None)
        
        assert len(agent.memory) == 1
        assert agent.memory[0] is None
    
    def test_empty_memory_operations(self):
        """Memory operations work correctly when memory is empty."""
        agent = ConcreteAgent("TestAgent")
        
        # Should not raise exceptions
        assert len(agent.memory) == 0
        assert agent.memory == []


class TestIntegrationScenarios:
    """Test realistic usage scenarios."""
    
    def test_full_agent_workflow(self):
        """Test complete agent workflow: setup, tool addition, execution, memory."""
        # Initialize agent
        agent = ConcreteAgent("WorkflowAgent", "Integration test agent")
        
        # Add tools
        calculator = CalculatorTool()
        agent.add_tool(calculator)
        
        # Execute query
        result = agent.execute("Calculate 2+2", {"session": "test"})
        
        # Store result in memory
        interaction = {
            "query": "Calculate 2+2",
            "result": result,
            "timestamp": "2024-01-01T12:00:00"
        }
        agent.add_to_memory(interaction)
        
        # Verify final state
        assert len(agent.tools) == 1
        assert len(agent.memory) == 1
        assert agent.get_available_tools() == ["calculator"]
        assert result["tools_used"] == ["calculator"]
    
    def test_agent_with_multiple_tools_and_interactions(self):
        """Test agent handling multiple tools and extended conversation."""
        agent = ConcreteAgent("MultiToolAgent")
        
        # Add multiple tools
        calc = CalculatorTool()
        mock_search = Mock()
        mock_search.name = "web_search"
        
        agent.add_tool(calc)
        agent.add_tool(mock_search)
        
        # Simulate multiple interactions
        queries = ["What is 2+2?", "Search for Python tutorials", "Calculate 10*5"]
        for i, query in enumerate(queries):
            result = agent.execute(query, {"turn": i})
            agent.add_to_memory({"query": query, "result": result})
        
        # Verify agent state
        assert len(agent.tools) == 2
        assert len(agent.memory) == 3
        assert set(agent.get_available_tools()) == {"calculator", "web_search"}


# Pytest fixtures for common test objects
@pytest.fixture
def sample_agent():
    """Fixture providing a basic ConcreteAgent for tests."""
    return ConcreteAgent("SampleAgent", "Agent for testing")


@pytest.fixture
def calculator_tool():
    """Fixture providing a CalculatorTool instance."""
    return CalculatorTool()


@pytest.fixture
def sample_interaction():
    """Fixture providing a sample interaction dictionary."""
    return {
        "query": "What is 2+2?",
        "response": "The answer is 4",
        "tools_used": ["calculator"],
        "timestamp": "2024-01-01T12:00:00"
    }


# Example parameterized test
@pytest.mark.parametrize("name,description,expected_name,expected_desc", [
    ("Agent1", "Description1", "Agent1", "Description1"),  # Normal case
    ("Agent2", "", "Agent2", ""),                          # Empty description
    ("", "NoName", "", "NoName"),                          # Empty name edge case
])
def test_agent_initialization_parameters(name, description, expected_name, expected_desc):
    """Test agent initialization with various parameter combinations."""
    agent = ConcreteAgent(name, description)
    assert agent.name == expected_name
    assert agent.description == expected_desc
