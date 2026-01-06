from __future__ import annotations

import json
import os
import requests
from pathlib import Path
from typing import Any, Dict

def call_llm_api(prompt: str, llm_cfg: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calls the configured LLM API with the given prompt and returns the JSON response.
    """
    api_key_env_var = llm_cfg.get("api_key_env_var")
    api_key = os.getenv(api_key_env_var) if api_key_env_var else None

    if not api_key:
        return {"ok": False, "error": f"API key environment variable '{api_key_env_var}' not set."}

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": llm_cfg.get("model"),
        "messages": [
            {"role": "system", "content": "You are an expert software developer. Your task is to complete the JSON object below to modify a codebase."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"}
    }

    endpoint_url = llm_cfg.get("endpoint_url")
    if not endpoint_url:
        return {"ok": False, "error": "LLM endpoint URL not configured."}

    try:
        response = requests.post(endpoint_url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        response_json = response.json()
        message_content = response_json.get("choices", [{}])[0].get("message", {}).get("content", "{}")
        
        # The content itself is a JSON string, so we need to parse it again
        parsed_content = json.loads(message_content)
        
        return {"ok": True, "response": parsed_content}

    except requests.RequestException as e:
        return {"ok": False, "error": f"API request failed: {e}"}
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        return {"ok": False, "error": f"Failed to parse LLM response: {e}"}
