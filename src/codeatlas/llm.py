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
    """Handles the specific request/response format for Google Gemini APIs."""
    model = llm_cfg.get("model", "gemini-1.5-flash")
    base_url = llm_cfg.get("endpoint_url", "https://generativelanguage.googleapis.com/v1beta/models")
    
    # Use header-based auth as specified
    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json"
    }
    url = f"{base_url.rstrip('/')}/{model}:generateContent"

    # Gemini requires a specific JSON body structure
    data = {
        "contents": [
            {"role": "user", "parts": [{"text": prompt}]}
        ],
        "generationConfig": {
            "response_mime_type": "application/json"
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=90)
        response.raise_for_status()
        response_json = response.json()
        
        # Concatenate text from all parts, as specified
        text_content = "".join(part["text"] for part in response_json["candidates"][0]["content"]["parts"])
        
        parsed_content = json.loads(text_content)
        return {"ok": True, "response": parsed_content}
    except requests.RequestException as e:
        return {"ok": False, "error": f"API request failed: {e}"}
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        return {"ok": False, "error": f"Failed to parse response: {e}"}

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
