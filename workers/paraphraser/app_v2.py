"""
Paraphraser Worker with Telemetry Support
kcloud - Paraphrasing for fluency and naturalness
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


app = FastAPI(title="Paraphraser Worker", version="2.0")

# Mount Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Load system prompt
PROMPT_PATH = os.environ.get("PROMPT_PATH", "/home/prompts/para.md")
with open(PROMPT_PATH, 'r') as f:
    PARA_SYS_FULL = f.read()

# Simplified prompt for runtime
PARA_SYS_RUNTIME = (
    "You are a paraphrasing agent. Rephrase the input for clarity and naturalness. "
    "Preserve the original meaning and intent. Make it more fluent and readable. "
    "Output only the paraphrased text."
)

HALLUCINATION_GUARD_PROMPT = (
    "You verify paraphrases for fidelity. Compare the original text with the paraphrased "
    "candidate. If the candidate introduces new facts or removes important details, rewrite it "
    "to stay faithful to the original. If you cannot keep it faithful, reply exactly "
    "'NO_SAFE_PARAPHRASE'."
)

# Config hash
CONFIG_HASH = hashlib.sha256(PARA_SYS_RUNTIME.encode()).hexdigest()[:12]


class ParaphraseRequest(BaseModel):
    text: str
    run_id: Optional[str] = None
    model: Optional[str] = "llama_3b"


class ParaphraseResponse(BaseModel):
    paraphrased: str
    latency_ms: float
    tokens: dict
    config_hash: str


@app.get("/health")
def health():
    """Health check endpoint."""
    return {
        "ok": True,
        "node": "paraphraser",
        "service": "paraphrasing",
        "config_hash": CONFIG_HASH
    }

async def guard_paraphrase(original: str, candidate: str) -> str:
    """Ensure paraphrase stays faithful to original content."""
    guard_messages = [
        {"role": "system", "content": HALLUCINATION_GUARD_PROMPT},
        {
            "role": "user",
            "content": (
                "Original text:\n"
                f"{original.strip()}\n\n"
                "Paraphrased candidate:\n"
                f"{candidate.strip()}"
            ),
        },
    ]
    guard = await chat(guard_messages, temperature=0.0, max_tokens=256)
    guard_text = guard["text"].strip()
    if guard_text.upper().startswith("NO_SAFE_PARAPHRASE"):
        return original
    return guard_text


@app.post("/paraphrase", response_model=ParaphraseResponse)
async def paraphrase(
    req: ParaphraseRequest,
    x_run_id: Optional[str] = Header(None),
    x_idempotency_key: Optional[str] = Header(None)
):
    """
    Paraphrase a text prompt for improved fluency.
    
    Headers:
        X-Run-Id: Optional run ID for tracking
        X-Idempotency-Key: Optional idempotency key
    """
    run_id = req.run_id or x_run_id
    
    with Timer("paraphraser", "paraphrase") as timer:
        # Prepare messages
        msgs = [
            {"role": "system", "content": PARA_SYS_RUNTIME},
            {"role": "user", "content": req.text},
        ]
        
        # Call vLLM
        out = await chat(msgs, temperature=0.3, max_tokens=512)
        
        candidate = out["text"]
        paraphrased_text = await guard_paraphrase(req.text, candidate)
        
        # Extract token usage from raw response
        raw = out.get("raw", {})
        usage = raw.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        
        # Record metrics
        record_tokens("paraphraser", input_tokens, output_tokens, req.model)
    
    tokens = {
        "input": input_tokens,
        "output": output_tokens
    }
    
    # Save artifacts if run_id provided
    if run_id:
        save_run_artifacts(
            run_id=run_id,
            node_name="paraphraser",
            input_data={"text": req.text},
            output_data={"paraphrased": paraphrased_text, "tokens": tokens},
            timing={"latency_ms": timer.elapsed_ms},
            config_hash=CONFIG_HASH
        )
    
    return ParaphraseResponse(
        paraphrased=paraphrased_text,
        latency_ms=timer.elapsed_ms,
        tokens=tokens,
        config_hash=CONFIG_HASH
    )


@app.get("/")
def root():
    """Root endpoint with service information."""
    return {
        "service": "Paraphraser Worker",
        "version": "2.0",
        "node": "kcloud",
        "model": "Llama-3.2-3B-Instruct + Paraphrase LoRA",
        "endpoints": {
            "POST /paraphrase": "Paraphrase text for fluency",
            "GET /health": "Health check",
            "GET /metrics": "Prometheus metrics"
        },
        "config_hash": CONFIG_HASH
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004, log_level="info")

