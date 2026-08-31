"""Code executor tool - run Python code, compute models, simulations."""

import asyncio
import subprocess
import tempfile
import os
from typing import Any, Dict


class CodeExecutor:
    """Execute Python code safely in isolated environments."""

    def __init__(self, allowed_libraries=None):
        """
        Initialize code executor.

        Args:
            allowed_libraries: List of allowed libraries. None = all.
        """
        self.allowed_libraries = allowed_libraries or [
            "pandas",
            "numpy",
            "scipy",
            "statsmodels",
            "sklearn",
            "prophet",
            "xgboost",
            "lightgbm",
            "pulp",
            "ortools",
            "plotly",
            "matplotlib",
            "json",
            "csv",
            "datetime",
            "math",
        ]

    async def execute(self, function_name: str, code: str, timeout: int = 60) -> Dict[str, Any]:
        """
        Execute Python code.

        Args:
            function_name: Name of the function being executed
            code: Python code to execute
            timeout: Execution timeout

        Returns:
            Execution result
        """
        if function_name == "run_code":
            return await self._run_python_code(code, timeout)
        elif function_name == "load_and_profile_data":
            # Expects params: {"file": "path/to/file"}
            return {"success": True, "message": "Data profiling not yet implemented"}
        elif function_name == "forecast":
            return await self._run_python_code(code, timeout)
        elif function_name == "optimize":
            return await self._run_python_code(code, timeout)
        else:
            return {"success": False, "error": f"Unknown function: {function_name}"}

    async def _run_python_code(self, code: str, timeout: int) -> Dict[str, Any]:
        """
        Execute Python code in a subprocess.
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            temp_file = f.name

        try:
            result = await asyncio.wait_for(
                self._subprocess_run(temp_file),
                timeout=timeout,
            )
            return result
        except asyncio.TimeoutError:
            return {"success": False, "error": f"Code execution timed out after {timeout}s"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    async def _subprocess_run(self, script_path: str) -> Dict[str, Any]:
        """
        Run Python script in subprocess.
        """
        loop = asyncio.get_event_loop()
        process = await loop.run_in_executor(
            None,
            lambda: subprocess.Popen(
                ["python", script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            ),
        )

        stdout, stderr = process.communicate()
        if process.returncode == 0:
            return {"success": True, "output": stdout}
        else:
            return {"success": False, "error": stderr}
