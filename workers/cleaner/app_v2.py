"""
Cleaner Worker with Telemetry Support
jw2 - Grammar correction and typo fixing
"""
import hashlib
import json
import os
from typing import Optional

from fastapi import FastAPI, Header
from pydantic import BaseModel
from prometheus_client import make_asgi_app

from mpr.common.vllm_client import chat
from mpr.common.persistence import save_run_artifacts
from mpr.telemetry.metrics import Timer, record_tokens


app = FastAPI(title="Cleaner Worker", version="2.0")

# Mount Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Load system prompt
PROMPT_PATH = os.environ.get("PROMPT_PATH", "/home/prompts/typo.md")
with open(PROMPT_PATH, 'r') as f:
    CLEAN_SYS = f.read()

# Simplified prompt for runtime
CLEAN_SYS_RUNTIME = (
    "You are a prompt-cleaning agent. Fix typos, casing, spacing, and grammar. "
    "Preserve meaning. Do NOT add new facts. Output only the corrected text."
)

HALLUCINATION_GUARD_PROMPT = (
    "You are a verification guard. Compare the original text with a cleaned candidate. "
    "Return the candidate only if it preserves all facts and intent. If the candidate "
    "introduces any new information, revert to the original wording (with minor fixes only). "
    "If nothing is safe, reply exactly with 'NO_SAFE_CLEAN'."
)

# Config hash
CONFIG_HASH = hashlib.sha256(CLEAN_SYS_RUNTIME.encode()).hexdigest()[:12]


class CleanRequest(BaseModel):
    text: str
    run_id: Optional[str] = None
    model: Optional[str] = "llama_3b"


class CleanResponse(BaseModel):
    cleaned: str
    latency_ms: float
    tokens: dict
    config_hash: str


@app.get("/health")
def health():
    """Health check endpoint."""
    return {
        "ok": True,
        "node": "cleaner",
        "service": "grammar_correction",
        "config_hash": CONFIG_HASH
    }

async def guard_cleaned(original: str, candidate: str) -> str:
    """Ensure cleaner output does not introduce new information."""
    guard_messages = [
        {"role": "system", "content": HALLUCINATION_GUARD_PROMPT},
        {
            "role": "user",
            "content": (
                "Original text:\n"
                f"{original.strip()}\n\n"
                "Cleaned candidate:\n"
                f"{candidate.strip()}"
            ),
        },
    ]
    guard = await chat(guard_messages, temperature=0.0, max_tokens=256)
    guard_text = guard["text"].strip()
    if guard_text.upper().startswith("NO_SAFE_CLEAN"):
        return original
    return guard_text


@app.post("/clean", response_model=CleanResponse)
async def clean(
    req: CleanRequest,
    x_run_id: Optional[str] = Header(None),
    x_idempotency_key: Optional[str] = Header(None)
):
    """
    Clean and correct a text prompt.
    
    Headers:
        X-Run-Id: Optional run ID for tracking
        X-Idempotency-Key: Optional idempotency key
    """
    run_id = req.run_id or x_run_id
    
    with Timer("cleaner", "clean") as timer:
        # Prepare messages
        msgs = [
            {"role": "system", "content": CLEAN_SYS_RUNTIME},
            {"role": "user", "content": req.text},
        ]
        
        # Call vLLM
        out = await chat(msgs, temperature=0.0, max_tokens=512)
        
        candidate = out["text"]
        cleaned_text = await guard_cleaned(req.text, candidate)
        
        # Extract token usage from raw response
        raw = out.get("raw", {})
        usage = raw.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        
        # Record metrics
        record_tokens("cleaner", input_tokens, output_tokens, req.model)
    
    tokens = {
        "input": input_tokens,
        "output": output_tokens
    }
    
    # Save artifacts if run_id provided
    if run_id:
        save_run_artifacts(
            run_id=run_id,
            node_name="cleaner",
            input_data={"text": req.text},
            output_data={"cleaned": cleaned_text, "tokens": tokens},
            timing={"latency_ms": timer.elapsed_ms},
            config_hash=CONFIG_HASH
        )
    
    return CleanResponse(
        cleaned=cleaned_text,
        latency_ms=timer.elapsed_ms,
        tokens=tokens,
        config_hash=CONFIG_HASH
    )


@app.get("/")
def root():
    """Root endpoint with service information."""
    return {
        "service": "Cleaner Worker",
        "version": "2.0",
        "node": "jw2",
        "model": "Llama-3.2-3B-Instruct + Grammar LoRA",
        "endpoints": {
            "POST /clean": "Clean and correct text",
            "GET /health": "Health check",
            "GET /metrics": "Prometheus metrics"
        },
        "config_hash": CONFIG_HASH
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")

