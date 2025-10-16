import os, time, httpx
from typing import Dict, Any, List

OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "http://localhost:8001/v1")
MODEL_NAME = os.environ.get("MODEL_NAME", "meta-llama/Llama-3.2-3B-Instruct")
TIMEOUT = float(os.environ.get("VLLM_TIMEOUT", "60"))

async def chat(messages: List[Dict[str,str]], temperature: float = 0.2, max_tokens: int = 512) -> Dict[str, Any]:
    """
    Call vLLM's OpenAI-compatible /v1/chat/completions.
    Returns: {'text': str, 'raw': full_json, 'latency_ms': float}
    """
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    t0 = time.perf_counter()
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.post(f"{OPENAI_BASE_URL}/chat/completions", json=payload)
        r.raise_for_status()
        data = r.json()
    text = data["choices"][0]["message"]["content"]
    return {"text": text, "raw": data, "latency_ms": (time.perf_counter() - t0) * 1000}
