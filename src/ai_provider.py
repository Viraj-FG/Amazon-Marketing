"""
AI Provider - Unified interface for local (Ollama) and cloud (OpenAI) models.
Defaults to FREE local Ollama models. Falls back to OpenAI if configured.
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# Configuration
# ============================================================

# Ollama (local, FREE)
OLLAMA_BASE_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

# OpenAI (cloud, paid) — only used if OPENAI_API_KEY is set
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Provider priority: ollama first (free), openai as fallback
USE_PROVIDER = os.getenv("AI_PROVIDER", "ollama")  # "ollama" or "openai"


# ============================================================
# Ollama (Local, Free)
# ============================================================

def ollama_generate(system_prompt, user_prompt, max_tokens=2000, temperature=0.75):
    """Generate text using local Ollama model"""
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature,
                },
                "stream": False,
            },
            timeout=300,  # Local models can be slow
        )
        response.raise_for_status()
        data = response.json()
        return data["message"]["content"]
    except requests.ConnectionError:
        print(f"[ERROR] Cannot connect to Ollama at {OLLAMA_BASE_URL}")
        print(f"[ERROR] Make sure Ollama is running: ollama serve")
        return None
    except Exception as e:
        print(f"[ERROR] Ollama generation failed: {e}")
        return None


def ollama_available():
    """Check if Ollama is running and model is available"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = [m["name"] for m in response.json().get("models", [])]
            if OLLAMA_MODEL in models or any(OLLAMA_MODEL.split(":")[0] in m for m in models):
                return True
            print(f"[WARN] Model '{OLLAMA_MODEL}' not found. Available: {models}")
            return False
    except:
        return False


# ============================================================
# OpenAI (Cloud, Paid)
# ============================================================

def openai_generate(system_prompt, user_prompt, max_tokens=2000, temperature=0.75):
    """Generate text using OpenAI API"""
    try:
        import openai
        openai.api_key = OPENAI_API_KEY

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"[ERROR] OpenAI generation failed: {e}")
        return None


# ============================================================
# Unified Interface
# ============================================================

def ai_generate(system_prompt, user_prompt, max_tokens=2000, temperature=0.75):
    """
    Generate text using the best available AI provider.
    Priority: Ollama (free) → OpenAI (paid fallback)
    """
    provider = USE_PROVIDER.lower()

    # Try Ollama first (free)
    if provider == "ollama" or (provider == "auto" and ollama_available()):
        print(f"  🦙 Using Ollama ({OLLAMA_MODEL})")
        result = ollama_generate(system_prompt, user_prompt, max_tokens, temperature)
        if result:
            return result
        print(f"  [WARN] Ollama failed, checking fallback...")

    # Fallback to OpenAI
    if OPENAI_API_KEY:
        print(f"  🌐 Using OpenAI (gpt-4o)")
        result = openai_generate(system_prompt, user_prompt, max_tokens, temperature)
        if result:
            return result

    print(f"  ❌ No AI provider available!")
    print(f"  → Start Ollama: ollama serve")
    print(f"  → Or set OPENAI_API_KEY in .env")
    return None


def get_provider_info():
    """Get info about current AI provider status"""
    info = {
        "provider": USE_PROVIDER,
        "ollama_url": OLLAMA_BASE_URL,
        "ollama_model": OLLAMA_MODEL,
        "ollama_available": ollama_available(),
        "openai_configured": bool(OPENAI_API_KEY),
    }
    return info


if __name__ == "__main__":
    # Quick test
    info = get_provider_info()
    print("AI Provider Status:")
    for k, v in info.items():
        print(f"  {k}: {v}")

    print("\nTest generation:")
    result = ai_generate(
        "You are helpful.",
        "Say 'Hello from Amazon Marketing!' in one sentence.",
        max_tokens=50,
    )
    print(f"Result: {result}")
