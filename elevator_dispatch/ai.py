from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib import error, request


@dataclass(frozen=True)
class AzureOpenAISettings:
    model: str = "gpt-4.1-mini"
    endpoint: str | None = None
    api_key: str | None = None
    deployment: str | None = None
    api_version: str = "2024-10-21"

    @classmethod
    def from_env(cls) -> "AzureOpenAISettings":
        return cls(
            model=os.getenv("AZURE_OPENAI_MODEL", "gpt-4.1-mini"),
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"),
        )

    @property
    def configured(self) -> bool:
        return bool(self.endpoint and self.api_key and self.deployment)


def build_ai_insight(
    settings: AzureOpenAISettings,
    dispatch_summary: dict[str, Any],
) -> dict[str, Any]:
    if not settings.configured:
        return {
            "source": "heuristic",
            "model": settings.model,
            "summary": (
                f"Using local predictive heuristics with model setting "
                f"'{settings.model}' until Azure OpenAI credentials are configured."
            ),
        }

    prompt = (
        "You are an elevator group controller. Summarize the dispatch choice in under "
        "60 words and list up to 2 predicted demand hotspots. Respond as JSON with "
        "keys 'summary' and 'hotspots'. "
        f"Dispatch summary: {json.dumps(dispatch_summary, separators=(',', ':'))}"
    )
    payload = {
        "messages": [
            {"role": "system", "content": "You optimize elevator traffic for office towers."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 180,
        "temperature": 0.2,
    }
    request_url = (
        f"{settings.endpoint.rstrip('/')}/openai/deployments/{settings.deployment}"
        f"/chat/completions?api-version={settings.api_version}"
    )
    http_request = request.Request(
        request_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "api-key": settings.api_key or "",
        },
        method="POST",
    )
    try:
        with request.urlopen(http_request, timeout=10) as response:
            body = json.loads(response.read().decode("utf-8"))
    except (TimeoutError, error.URLError, json.JSONDecodeError):
        return {
            "source": "heuristic",
            "model": settings.model,
            "summary": "Azure OpenAI was unavailable, so the dispatcher used local predictive heuristics.",
        }

    try:
        content = body["choices"][0]["message"]["content"]
        parsed_content = json.loads(content)
    except (KeyError, IndexError, TypeError, json.JSONDecodeError):
        return {
            "source": "heuristic",
            "model": settings.model,
            "summary": "Azure OpenAI returned an unreadable response, so local heuristics were used.",
        }

    return {
        "source": "azure-openai",
        "model": settings.model,
        "summary": parsed_content.get("summary", "Dispatch recommendation generated."),
        "hotspots": parsed_content.get("hotspots", []),
    }
