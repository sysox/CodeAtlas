from __future__ import annotations

import json
import os
import requests
from typing import Any, Dict

def call_llm_api(prompt: str, llm_cfg: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calls the configured LLM API with the given prompt and returns the JSON response.
    Supports 'openai' and 'gemini' providers.
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

def _call_openai(prompt: str, api_key: str, llm_cfg: Dict[str, Any]) -> Dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    endpoint_url = llm_cfg.get("endpoint_url", "https://api.openai.com/v1/chat/completions")
    model = llm_cfg.get("model", "gpt-4-turbo-preview")

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are an expert software developer. Your task is to complete the JSON object below to modify a codebase."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"}
    }

    try:
        response = requests.post(endpoint_url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        response_json = response.json()
        message_content = response_json.get("choices", [{}])[0].get("message", {}).get("content", "{}")
        
        parsed_content = json.loads(message_content)
        return {"ok": True, "response": parsed_content}

    except requests.RequestException as e:
        return {"ok": False, "error": f"OpenAI API request failed: {e}"}
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        return {"ok": False, "error": f"Failed to parse OpenAI response: {e}"}

def _call_gemini(prompt: str, api_key: str, llm_cfg: Dict[str, Any]) -> Dict[str, Any]:
    model = llm_cfg.get("model", "gemini-pro")
    base_url = llm_cfg.get("endpoint_url", "https://generativelanguage.googleapis.com/v1beta/models")
    
    # Explicitly construct the URL for v1beta
    # Ensure no double slashes
    base_url = base_url.rstrip('/')
    url = f"{base_url}/{model}:generateContent?key={api_key}"

    # Debug print (masked key)
    # print(f"DEBUG: Calling Gemini URL: {url.replace(api_key, 'HIDDEN')}")

    headers = {"Content-Type": "application/json"}
    
    full_prompt = f"You are an expert software developer. Return ONLY a valid JSON object.\n\n{prompt}"

    data = {
        "contents": [{
            "parts": [{"text": full_prompt}]
        }],
        "generationConfig": {
            "response_mime_type": "application/json"
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        response_json = response.json()
        try:
            text_content = response_json["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
             return {"ok": False, "error": f"Unexpected Gemini response format: {response_json}"}

        parsed_content = json.loads(text_content)
        return {"ok": True, "response": parsed_content}

    except requests.RequestException as e:
        return {"ok": False, "error": f"Gemini API request failed: {e}"}
    except json.JSONDecodeError as e:
        return {"ok": False, "error": f"Failed to parse Gemini JSON response: {e}\nRaw text: {text_content}"}
