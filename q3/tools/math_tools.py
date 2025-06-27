"""
Math tools for the tool-enhanced reasoning script.
Provides mathematical operations that can be called by the LLM.
"""

import math
from typing import Union, List


def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    return a - b


def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


def divide(a: float, b: float) -> float:
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def power(base: float, exponent: float) -> float:
    """Raise base to the power of exponent."""
    return base ** exponent


def square_root(number: float) -> float:
    """Calculate the square root of a number."""
    if number < 0:
        raise ValueError("Cannot calculate square root of negative number")
    return math.sqrt(number)


def average(numbers: List[float]) -> float:
    """Calculate the average of a list of numbers."""
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")
    return sum(numbers) / len(numbers)


def median(numbers: List[float]) -> float:
    """Calculate the median of a list of numbers."""
    if not numbers:
        raise ValueError("Cannot calculate median of empty list")
    sorted_numbers = sorted(numbers)
    n = len(sorted_numbers)
    if n % 2 == 0:
        return (sorted_numbers[n//2 - 1] + sorted_numbers[n//2]) / 2
    else:
        return sorted_numbers[n//2]


def maximum(numbers: List[float]) -> float:
    """Find the maximum value in a list of numbers."""
    if not numbers:
        raise ValueError("Cannot find maximum of empty list")
    return max(numbers)


def minimum(numbers: List[float]) -> float:
    """Find the minimum value in a list of numbers."""
    if not numbers:
        raise ValueError("Cannot find minimum of empty list")
    return min(numbers)


def factorial(n: int) -> int:
    """Calculate the factorial of a non-negative integer."""
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    return math.factorial(n)


def absolute_value(number: float) -> float:
    """Calculate the absolute value of a number."""
    return abs(number)


def round_number(number: float, decimals: int = 0) -> float:
    """Round a number to specified decimal places."""
    return round(number, decimals)


def percentage(part: float, whole: float) -> float:
    """Calculate what percentage 'part' is of 'whole'."""
    if whole == 0:
        raise ValueError("Cannot calculate percentage with zero as whole")
    return (part / whole) * 100


def calculate_expression(expression: str) -> float:
    """
    Safely evaluate a mathematical expression.
    Only allows basic mathematical operations for security.
    """
    # Remove whitespace
    expression = expression.replace(" ", "")
    
    # Only allow safe characters
    allowed_chars = set("0123456789+-*/().sqrt")
    if not all(c in allowed_chars for c in expression.lower()):
        raise ValueError("Expression contains invalid characters")
    
    # Replace sqrt with math.sqrt
    expression = expression.replace("sqrt", "math.sqrt")
    
    # Evaluate safely (in a real application, you'd want more robust parsing)
    try:
        # This is a simplified approach - in production, use a proper expression parser
        result = eval(expression, {"__builtins__": {}, "math": math})
        return float(result)
    except Exception as e:
        raise ValueError(f"Invalid mathematical expression: {e}")


# Tool registry for easy access
MATH_TOOLS = {
    "add": add,
    "subtract": subtract,
    "multiply": multiply,
    "divide": divide,
    "power": power,
    "square_root": square_root,
    "average": average,
    "median": median,
    "maximum": maximum,
    "minimum": minimum,
    "factorial": factorial,
    "absolute_value": absolute_value,
    "round_number": round_number,
    "percentage": percentage,
    "calculate_expression": calculate_expression
}


def get_available_tools() -> List[str]:
    """Get a list of available math tools."""
    return list(MATH_TOOLS.keys())


def call_tool(tool_name: str, *args, **kwargs) -> Union[float, int]:
    """Call a math tool by name with given arguments."""
    if tool_name not in MATH_TOOLS:
        raise ValueError(f"Unknown math tool: {tool_name}")
    
    try:
        return MATH_TOOLS[tool_name](*args, **kwargs)
    except Exception as e:
        raise ValueError(f"Error calling {tool_name}: {e}")
