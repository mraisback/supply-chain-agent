"""File system tool - read/write Excel, CSV, JSON, Parquet."""

import os
import json
import csv
from typing import Any, Dict, List, Optional
import pandas as pd


class FileSystemClient:
    """Client for file system operations."""

    def __init__(self, base_path: str = "."):
        self.base_path = base_path

    async def execute(self, function_name: str, **params) -> Dict[str, Any]:
        """
        Execute file operations.

        Args:
            function_name: Operation name (read, write, list, etc.)
            **params: Operation parameters

        Returns:
            Operation result
        """
        if function_name == "read_csv":
            return await self._read_csv(params.get("path", ""))
        elif function_name == "read_excel":
            return await self._read_excel(params.get("path", ""), params.get("sheet"))
        elif function_name == "read_json":
            return await self._read_json(params.get("path", ""))
        elif function_name == "write_csv":
            return await self._write_csv(params.get("path", ""), params.get("data", []))
        elif function_name == "write_excel":
            return await self._write_excel(params.get("path", ""), params.get("data", []))
        elif function_name == "write_json":
            return await self._write_json(params.get("path", ""), params.get("data", {}))
        elif function_name == "list_files":
            return await self._list_files(params.get("path", ""))
        else:
            return {"success": False, "error": f"Unknown function: {function_name}"}

    async def _read_csv(self, path: str) -> Dict[str, Any]:
        """Read CSV file."""
        try:
            full_path = os.path.join(self.base_path, path)
            df = pd.read_csv(full_path)
            return {
                "success": True,
                "data": df.to_dict(orient="records"),
                "shape": df.shape,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _read_excel(self, path: str, sheet: Optional[str] = None) -> Dict[str, Any]:
        """Read Excel file."""
        try:
            full_path = os.path.join(self.base_path, path)
            df = pd.read_excel(full_path, sheet_name=sheet)
            return {
                "success": True,
                "data": df.to_dict(orient="records"),
                "shape": df.shape,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _read_json(self, path: str) -> Dict[str, Any]:
        """Read JSON file."""
        try:
            full_path = os.path.join(self.base_path, path)
            with open(full_path, "r") as f:
                data = json.load(f)
            return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _write_csv(self, path: str, data: List[Dict]) -> Dict[str, Any]:
        """Write CSV file."""
        try:
            full_path = os.path.join(self.base_path, path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            df = pd.DataFrame(data)
            df.to_csv(full_path, index=False)
            return {"success": True, "message": f"Wrote {len(data)} rows to {path}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _write_excel(self, path: str, data: List[Dict]) -> Dict[str, Any]:
        """Write Excel file."""
        try:
            full_path = os.path.join(self.base_path, path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            df = pd.DataFrame(data)
            df.to_excel(full_path, index=False)
            return {"success": True, "message": f"Wrote {len(data)} rows to {path}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _write_json(self, path: str, data: Dict) -> Dict[str, Any]:
        """Write JSON file."""
        try:
            full_path = os.path.join(self.base_path, path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                json.dump(data, f, indent=2)
            return {"success": True, "message": f"Wrote JSON to {path}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _list_files(self, path: str = "") -> Dict[str, Any]:
        """List files in directory."""
        try:
            full_path = os.path.join(self.base_path, path)
            files = os.listdir(full_path)
            return {"success": True, "files": files, "count": len(files)}
        except Exception as e:
            return {"success": False, "error": str(e)}
