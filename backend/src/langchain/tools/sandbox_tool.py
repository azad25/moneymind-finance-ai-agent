"""
Sandbox MCP Tool
LangChain tool for secure code execution via sandbox-mcp
"""
from typing import Optional
from langchain_core.tools import tool
import httpx

from src.config.settings import settings


@tool
async def execute_python_code(
    code: str,
    description: Optional[str] = None,
) -> str:
    """
    Execute Python code in a secure sandbox environment.
    
    Use this for:
    - Mathematical calculations
    - Data transformations
    - Financial computations
    - Chart data generation
    
    Args:
        code: Python code to execute (must be valid Python 3.11)
        description: Optional description of what the code does
    
    Returns:
        The output of the code execution or error message
    
    Example:
        execute_python_code("print(sum([100, 200, 300]))")
        -> "600"
    """
    if not settings.sandbox_mcp_url:
        return "❌ Sandbox execution is not configured."
    
    # Basic code validation
    if not code or not code.strip():
        return "❌ No code provided."
    
    # Check for dangerous operations
    dangerous_keywords = [
        "import os",
        "import sys",
        "import subprocess",
        "open(",
        "__import__",
        "exec(",
        "eval(",
        "compile(",
    ]
    
    for keyword in dangerous_keywords:
        if keyword in code.lower():
            return f"❌ Code contains disallowed operation: {keyword}"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.sandbox_mcp_url}/execute",
                json={
                    "code": code,
                    "language": "python",
                    "timeout": 10,  # 10 second timeout
                },
            )
            
            if response.status_code == 200:
                result = response.json()
                output = result.get("output", "")
                error = result.get("error", "")
                
                if error:
                    return f"❌ **Execution Error:**\n```\n{error}\n```"
                
                return f"✅ **Result:**\n```\n{output}\n```"
            else:
                return f"❌ Sandbox error: {response.status_code}"
                
    except httpx.TimeoutException:
        return "❌ Code execution timed out (max 10 seconds)."
    except Exception as e:
        return f"❌ Sandbox execution failed: {str(e)}"


@tool
async def calculate_expression(expression: str) -> str:
    """
    Calculate a mathematical expression safely.
    
    Args:
        expression: Mathematical expression (e.g., "100 * 1.08", "1000 / 12")
    
    Returns:
        The result of the calculation
    """
    import ast
    import operator
    
    # Allowed operators
    operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
    }
    
    def eval_expr(node):
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            return operators[type(node.op)](eval_expr(node.left), eval_expr(node.right))
        elif isinstance(node, ast.UnaryOp):
            return operators[type(node.op)](eval_expr(node.operand))
        else:
            raise ValueError(f"Unsupported expression: {node}")
    
    try:
        tree = ast.parse(expression, mode='eval')
        result = eval_expr(tree.body)
        return f"🧮 **{expression}** = **{result:,.4f}**"
    except Exception as e:
        return f"❌ Calculation error: {str(e)}"


# Export tools
sandbox_tools = [
    execute_python_code,
    calculate_expression,
]
