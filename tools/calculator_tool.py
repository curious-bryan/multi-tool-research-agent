# tools/calculator_tool.py
"""Calculator tool for performing mathematical operations in AI agent systems."""

import operator
from typing import Union, Dict, Any, Literal

class CalculatorTool:
    """
    Calculator tool for AI agent systems.

    This tool provides basic mathematical calculation capabilities for agents
    that need to perform arithmetic operations. It implements the standard
    tool interface expected by the agent framework.

    Note: This is a basic implementation suitable for simple calculations.
    For advanced math operations, consider integrating with NumPy.

    Supported operations:
    - Basic arithmetic: +, -, *, /, **, %
    - Parentheses for grouping: (2 + 3) * 4
    - Numbers: integers, floats, scientific notation

    Example:
        >>> calc = CalculatorTool()
        >>> calc.calculate("2 + 3")
        {'success': True, 'result': 5, 'expression': '2 + 3', 'tool': 'calculator'}

    Limitations:
    - No support for mathematical functions (sin, cos, log, etc.)
    - No variable assignment or memory
    - Expression length limited by Python's eval constraints
    - Security: Not suitable for user-facing applications without sandboxing
    """
    
    
    def __init__(self):
        self.name = "calculator"
        self.description = "Performs basic mathematical operations"
        self.operations = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv,
            '**': operator.pow,
            '%': operator.mod
        }
    
    def calculate(self, expression: str) -> Dict[Literal["success", "result", "error", "expression", "tool"], Any]:
        """
        Calculate the result of a mathematical expression.
        
        Args:
            expression: Mathematical expression as a string (e.g., "2 + 3 * 4", "10 / 2")
            
        Returns:
            Dictionary with result and metadata:
            - success (bool): Whether calculation succeeded
            - result (float): The calculated result (if successful)
            - error (str): Error message (if failed)
            - expression (str): Original expression
            - tool (str): Tool name identifier

        Common errors:
        - Division by zero: "5 / 0"
        - Invalid syntax: "2 + + 3" 
        - Unsupported functions: "sin(30)"
        """

        try:
            # WARNING: Uses eval() for expression parsing. 
            # Not safe for untrusted input in production environments.
            # Consider using a proper math parser.
            result = eval(expression, {"__builtins__": {}}, {})
            return {
                "success": True,
                "result": result,
                "expression": expression,
                "tool": self.name
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "expression": expression,
                "tool": self.name
            }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the calculator tool with the standard agent interface.
        
        Args:
            **kwargs: Keyword arguments, expects 'expression' key with math expression
            
        Returns:
            Dictionary containing the calculation result (same format as calculate())
            
        Example:
            >>> calc.execute(expression="5 * 6")
            {'success': True, 'result': 30, 'expression': '5 * 6', 'tool': 'calculator'}
        """
        expression = kwargs.get('expression', '')
        return self.calculate(expression)