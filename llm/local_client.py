"""
Local LLM Client

Thin wrapper around a local HTTP LLM server (e.g. Ollama).
This keeps all language-model processing on your machine.
"""

from __future__ import annotations

import os
from typing import List, Dict

import requests


class LocalLLMClient:
    """
    Minimal chat client for a local LLM server.

    By default it targets Ollama:
      - base_url: http://localhost:11434
      - endpoint: POST /api/chat
      - payload: {"model": "<model>", "messages": [...]}
    """

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 20.0,
    ) -> None:
        self.base_url = base_url or os.getenv("LLM_BASE_URL", "http://localhost:11434")
        self.model = model or os.getenv("LLM_MODEL", "llama3.2")
        self.timeout = timeout

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Send a chat conversation and return the assistant's reply text.

        messages: list of {"role": "system"|"user"|"assistant", "content": str}
        """
        url = f"{self.base_url.rstrip('/')}/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
        }

        resp = requests.post(url, json=payload, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()

        # Ollama returns {"message": {"role": "...", "content": "..."}}
        msg = data.get("message") or {}
        content = msg.get("content", "")
        return content.strip()

