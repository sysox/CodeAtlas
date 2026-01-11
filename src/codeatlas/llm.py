from __future__ import annotations

import json
import os
import requests
from typing import Any, Dict

def _call_openai(prompt: str, api_key: str, llm_cfg: Dict[str, Any]) -> Dict[str, Any]:
    """Handles the specific request/response format for OpenAI APIs."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    endpoint_url = llm_cfg.get("endpoint_url", "https://api.openai.com/v1/chat/completions")
    model = llm_cfg.get("model", "gpt-4-turbo")

    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }

    try:
        response = requests.post(endpoint_url, headers=headers, json=data, timeout=90)
        response.raise_for_status()
        response_json = response.json()
        message_content = response_json["choices"][0]["message"]["content"]
        parsed_content = json.loads(message_content)
        return {"ok": True, "response": parsed_content}
    except requests.RequestException as e:
        return {"ok": False, "error": f"API request failed: {e}"}
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        return {"ok": False, "error": f"Failed to parse response: {e}"}

def _call_gemini(prompt: str, api_key: str, llm_cfg: Dict[str, Any]) -> Dict[str, Any]:
    """Handles the specific request/response format for Google Gemini APIs (REST v1beta)."""
    # Use a currently supported default model (override via llm_cfg["model"])
    model = llm_cfg.get("model", "gemini-2.0-flash")

    # Base REST endpoint for models
    base_url = llm_cfg.get("endpoint_url", "https://generativelanguage.googleapis.com/v1beta/models")
    url = f"{base_url.rstrip('/')}/{model}:generateContent"

    # Header-based auth
    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json",
    }

    # Gemini request body structure
    data = {
        "contents": [
            {"role": "user", "parts": [{"text": prompt}]}
        ],
        "generationConfig": {
            # IMPORTANT: camelCase keys for REST
            "responseMimeType": "application/json",
            # Optional: enforce JSON more strongly (keeps it schema-light)
            "responseJsonSchema": {"type": "object"},
        },
    }

    def _parse_response(response_json: Dict[str, Any]) -> Dict[str, Any]:
        # Concatenate text from all parts
        candidates = response_json.get("candidates") or []
        if not candidates:
            return {"ok": False, "error": f"Gemini response missing candidates: {response_json}"}
        content = (candidates[0].get("content") or {})
        parts = content.get("parts") or []
        text_content = "".join((p.get("text") or "") for p in parts).strip()
        if not text_content:
            return {"ok": False, "error": f"Gemini response missing text parts: {response_json}"}
        try:
            parsed_content = json.loads(text_content)
        except json.JSONDecodeError as e:
            snippet = text_content[:500]
            return {"ok": False, "error": f"Failed to parse JSON from Gemini: {e}; text[:500]={snippet!r}"}
        return {"ok": True, "response": parsed_content}

    try:
        response = requests.post(url, headers=headers, json=data, timeout=90)
        response.raise_for_status()
        return _parse_response(response.json())

    except requests.RequestException as e:
        # Fallback: some environments prefer query-param API key
        try:
            fallback_url = f"{url}?key={api_key}"
            response = requests.post(fallback_url, headers={"Content-Type": "application/json"}, json=data, timeout=90)
            response.raise_for_status()
            return _parse_response(response.json())
        except requests.RequestException:
            return {"ok": False, "error": f"API request failed: {e}"}

def call_llm_api(prompt: str, llm_cfg: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calls the configured LLM API with the given prompt and returns the JSON response.
    Supports 'openai' and 'gemini' providers by dispatching to the correct handler.
    """
    provider = llm_cfg.get("provider", "openai").lower()
    api_key_env_var = llm_cfg.get("api_key_env_var")
    api_key = os.getenv(api_key_env_var) if api_key_env_var else None

    if not api_key:
        return {"ok": False, "error": f"API key environment variable '{api_key_env_var}' not set."}

    if provider == "openai":
        return _call_openai(prompt, api_key, llm_cfg)
    elif provider == "gemini":
        return _call_gemini(prompt, api_key, llm_cfg)
    else:
        return {"ok": False, "error": f"Unsupported provider: {provider}"}
