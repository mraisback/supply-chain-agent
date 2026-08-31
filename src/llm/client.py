"""Llama LLM client integration."""

import aiohttp
import json
from typing import Any, Dict, Optional
import os
from datetime import datetime


class LlamaClient:
    """Client for interacting with Llama models via Ollama or API."""

    def __init__(
        self,
        api_base: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ):
        """
        Initialize Llama client.

        Args:
            api_base: API base URL (e.g., http://localhost:11434)
            model: Model name (e.g., llama2:7b)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
        """
        self.api_base = api_base or os.getenv("LLAMA_API_BASE", "http://localhost:11434")
        self.model = model or os.getenv("LLAMA_MODEL", "llama2:7b")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.call_history: list = []

    async def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Generate text using Llama model.

        Args:
            prompt: Input prompt
            temperature: Optional override for temperature
            max_tokens: Optional override for max tokens
            system_prompt: System prompt to set context

        Returns:
            Generated text
        """
        temp = temperature or self.temperature
        tokens = max_tokens or self.max_tokens

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temp,
            "num_predict": tokens,
            "stream": False,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/api/chat",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=300),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        response_text = data["message"]["content"]
                        
                        # Log the call
                        self.call_history.append({
                            "timestamp": datetime.utcnow().isoformat(),
                            "prompt": prompt[:100],
                            "response": response_text[:100],
                            "model": self.model,
                        })
                        
                        return response_text
                    else:
                        error_text = await resp.text()
                        raise Exception(f"API error {resp.status}: {error_text}")
        except aiohttp.ClientConnectorError:
            raise Exception(
                f"Could not connect to Llama API at {self.api_base}. "
                "Make sure Ollama is running: ollama serve"
            )
        except Exception as e:
            raise Exception(f"Error calling Llama API: {str(e)}")

    async def generate_with_schema(
        self,
        prompt: str,
        schema: Dict[str, Any],
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate JSON response matching a schema.

        Args:
            prompt: Input prompt
            schema: JSON schema for response
            system_prompt: System prompt

        Returns:
            Parsed JSON response
        """
        schema_str = json.dumps(schema, indent=2)
        prompt_with_schema = f"""{prompt}

Return your response as valid JSON matching this schema:
{schema_str}
"""

        response_text = await self.generate(prompt_with_schema, system_prompt=system_prompt)
        
        try:
            # Try to extract JSON from response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                return {"error": "Could not find JSON in response", "raw": response_text}
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON in response: {str(e)}", "raw": response_text}

    def get_call_history(self) -> list:
        """Get history of LLM calls."""
        return self.call_history

    def clear_history(self):
        """Clear call history."""
        self.call_history = []
