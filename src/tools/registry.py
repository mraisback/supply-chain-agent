"""Tool system - registry and execution framework."""

import asyncio
from typing import Any, Dict, Callable, Optional, List
from functools import wraps


class ToolRegistry:
    """Registry for tools available to agents."""

    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}

    def register(self, tool_name: str, description: str = ""):
        """
        Decorator to register a tool.

        Args:
            tool_name: Name of the tool
            description: Description of what the tool does
        """
        def decorator(func: Callable) -> Callable:
            self.tools[tool_name] = {
                "name": tool_name,
                "description": description,
                "function": func,
                "callable": True,
            }

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)

            return async_wrapper

        return decorator

    async def execute(self, tool_name: str, function_name: str, params: Dict[str, Any], timeout: int = 300) -> Dict[str, Any]:
        """
        Execute a tool function.

        Args:
            tool_name: Name of the tool
            function_name: Function within the tool
            params: Parameters to pass
            timeout: Execution timeout in seconds

        Returns:
            Result of execution
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")

        tool = self.tools[tool_name]
        func = tool["function"]

        try:
            if asyncio.iscoroutinefunction(func):
                result = await asyncio.wait_for(func(function_name, **params), timeout=timeout)
            else:
                result = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(None, func, function_name, **params),
                    timeout=timeout,
                )
            return {"success": True, "result": result}
        except asyncio.TimeoutError:
            return {"success": False, "error": f"Tool execution timed out after {timeout}s"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_tools(self) -> List[Dict[str, str]]:
        """List all registered tools."""
        return [
            {"name": name, "description": tool["description"]}
            for name, tool in self.tools.items()
        ]
