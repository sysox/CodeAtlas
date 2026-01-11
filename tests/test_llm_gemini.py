from __future__ import annotations

import json
from typing import Any, Dict

import codeatlas.llm as llm


class _DummyResponse:
    def __init__(self, payload: Dict[str, Any], status_code: int = 200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")

    def json(self) -> Dict[str, Any]:
        return self._payload


def test_call_gemini_parses_json_object(monkeypatch):
    # Arrange: mock requests.post to return a valid Gemini REST response
    def _fake_post(url, headers=None, json=None, timeout=None):
        assert url.endswith(":generateContent")
        assert "x-goog-api-key" in (headers or {})
        # Ensure we request JSON output (camelCase)
        gen = (json or {}).get("generationConfig") or {}
        assert gen.get("responseMimeType") == "application/json"

        payload = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": "{\"ok\": true, \"x\": 1}"}
                        ]
                    }
                }
            ]
        }
        return _DummyResponse(payload)

    monkeypatch.setattr(llm.requests, "post", _fake_post)

    out = llm._call_gemini(
        prompt="return json",
        api_key="DUMMY",
        llm_cfg={
            "provider": "gemini",
            "model": "gemini-2.5-flash",
            "endpoint_url": "https://generativelanguage.googleapis.com/v1beta/models",
        },
    )
    assert out["ok"] is True
    assert out["response"] == {"ok": True, "x": 1}


def test_call_gemini_handles_non_json(monkeypatch):
    # Arrange: Gemini returns text that is not JSON → we should fail cleanly
    def _fake_post(url, headers=None, json=None, timeout=None):
        payload = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": "not json"}
                        ]
                    }
                }
            ]
        }
        return _DummyResponse(payload)

    monkeypatch.setattr(llm.requests, "post", _fake_post)

    out = llm._call_gemini(
        prompt="return json",
        api_key="DUMMY",
        llm_cfg={"provider": "gemini"},
    )
    assert out["ok"] is False
    assert "Failed to parse" in out["error"] or "Failed to parse JSON" in out["error"]
