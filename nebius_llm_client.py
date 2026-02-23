import os

import requests
from requests import exceptions as requests_exceptions
from fastapi import HTTPException

from constants import REQUEST_TIMEOUT


class NebiusLLMClient:
    def __init__(self, timeout: int = REQUEST_TIMEOUT):
        self.api_key = os.getenv("NEBIUS_API_KEY") or os.getenv("NUBEUS_API_KEY")
        if not self.api_key:
            raise HTTPException(status_code=500, detail="NEBIUS_API_KEY is not set")
        self.base_url = os.getenv("NEBIUS_API_BASE", "https://api.tokenfactory.nebius.com/v1")
        self.model = os.getenv("NEBIUS_MODEL", "meta-llama/Llama-3.3-70B-Instruct")
        self.timeout = timeout

    def chat(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a concise software analyst."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 600,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )
        except requests_exceptions.ReadTimeout as exc:
            raise HTTPException(
                status_code=504,
                detail="LLM provider timed out. Try again or increase REQUEST_TIMEOUT.",
            ) from exc
        if response.status_code == 401:
            raise HTTPException(
                status_code=401,
                detail=f"Invalid NEBIUS_API_KEY: {response.text[:300]}",
            )
        if response.status_code >= 400:
            raise HTTPException(
                status_code=502,
                detail=f"LLM provider error ({response.status_code}): {response.text[:300]}",
            )

        data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise HTTPException(status_code=502, detail="Unexpected LLM response format") from exc
