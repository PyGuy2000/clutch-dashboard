"""Ollama API helper for querying running and available models on AI Workstation."""

import os
import urllib.request
import json

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://192.168.1.50:11434")


def _get(path):
    """Make a GET request to the Ollama API."""
    try:
        url = f"{OLLAMA_URL}{path}"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


def running_models():
    """Get currently loaded/running models with VRAM usage."""
    data = _get("/api/ps")
    if not data:
        return []
    models = []
    for m in data.get("models", []):
        models.append({
            "name": m.get("name", ""),
            "size": m.get("size", 0),
            "size_gb": round(m.get("size", 0) / 1024 / 1024 / 1024, 1),
            "vram_gb": round(m.get("size_vram", 0) / 1024 / 1024 / 1024, 1),
            "expires_at": m.get("expires_at", ""),
        })
    return models


def available_models():
    """Get all locally available models."""
    data = _get("/api/tags")
    if not data:
        return []
    models = []
    for m in data.get("models", []):
        models.append({
            "name": m.get("name", ""),
            "size_gb": round(m.get("size", 0) / 1024 / 1024 / 1024, 1),
            "modified_at": m.get("modified_at", ""),
            "family": m.get("details", {}).get("family", ""),
            "parameter_size": m.get("details", {}).get("parameter_size", ""),
            "quantization": m.get("details", {}).get("quantization_level", ""),
        })
    return models


def ollama_health():
    """Check if Ollama is responding."""
    try:
        url = f"{OLLAMA_URL}/api/tags"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status == 200
    except Exception:
        return False
