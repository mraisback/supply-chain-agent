"""API client tool - HTTP requests, webhooks, integrations."""

import aiohttp
import json
from typing import Any, Dict, Optional


class APIClient:
    """Client for making HTTP API calls."""

    def __init__(self, base_url: Optional[str] = None, headers: Optional[Dict] = None):
        self.base_url = base_url or ""
        self.default_headers = headers or {"Content-Type": "application/json"}

    async def execute(self, function_name: str, **params) -> Dict[str, Any]:
        """
        Execute API operations.

        Args:
            function_name: Operation name (get, post, put, delete, etc.)
            **params: Request parameters

        Returns:
            API response
        """
        if function_name == "get":
            return await self._get(params)
        elif function_name == "post":
            return await self._post(params)
        elif function_name == "put":
            return await self._put(params)
        elif function_name == "delete":
            return await self._delete(params)
        else:
            return {"success": False, "error": f"Unknown function: {function_name}"}

    async def _get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """GET request."""
        url = params.get("url", "")
        if self.base_url and not url.startswith("http"):
            url = f"{self.base_url}/{url}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.default_headers) as resp:
                    data = await resp.json()
                    return {"success": True, "status": resp.status, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _post(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """POST request."""
        url = params.get("url", "")
        payload = params.get("data", {})

        if self.base_url and not url.startswith("http"):
            url = f"{self.base_url}/{url}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    headers=self.default_headers,
                ) as resp:
                    data = await resp.json()
                    return {"success": True, "status": resp.status, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _put(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """PUT request."""
        url = params.get("url", "")
        payload = params.get("data", {})

        if self.base_url and not url.startswith("http"):
            url = f"{self.base_url}/{url}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.put(
                    url,
                    json=payload,
                    headers=self.default_headers,
                ) as resp:
                    data = await resp.json()
                    return {"success": True, "status": resp.status, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """DELETE request."""
        url = params.get("url", "")

        if self.base_url and not url.startswith("http"):
            url = f"{self.base_url}/{url}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(url, headers=self.default_headers) as resp:
                    return {"success": True, "status": resp.status}
        except Exception as e:
            return {"success": False, "error": str(e)}
