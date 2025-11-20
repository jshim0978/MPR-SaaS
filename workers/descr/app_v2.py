"""
Describer Worker with Telemetry Support
jw3 - Knowledge expansion and context addition
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


app = FastAPI(title="Describer Worker", version="2.0")

# Mount Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Load system prompt
PROMPT_PATH = os.environ.get("PROMPT_PATH", "/home/prompts/descr.md")
with open(PROMPT_PATH, 'r') as f:
    DESCR_SYS_FULL = f.read()

# Simplified prompt for runtime
DESCR_SYS_RUNTIME = (
    "You are a description-generating agent. Given a user query, add short, useful context: "
    "clarify ambiguous terms, list key entities or subtopics, and expand acronyms. "
    "Output a JSON specification first:\n"
    '{\n  "task": "...",\n  "entities": [...],\n  "constraints": [...],\n  "acceptance_criteria": [...]\n}\n'
    "Then a concise summary (≤120 words) with encyclopedic context. "
    "Do NOT invent facts; stay grounded only in the provided text."
)

HALLUCINATION_GUARD_PROMPT = (
    "You are a careful fact-checking guard. Compare the original user prompt with a candidate "
    "description. Remove or rewrite any statement that cannot be directly inferred from the "
    "user prompt. If nothing remains fully supported, reply with exactly 'NO_SUPPORTED_CONTEXT'. "
    "Never add new information."
)

# Config hash
CONFIG_HASH = hashlib.sha256(DESCR_SYS_RUNTIME.encode()).hexdigest()[:12]


class DescribeRequest(BaseModel):
    text: str
    run_id: Optional[str] = None
    model: Optional[str] = "llama_3b"


class DescribeResponse(BaseModel):
    description: str
    json_spec: Optional[dict] = None
    latency_ms: float
    tokens: dict
    config_hash: str


@app.get("/health")
def health():
    """Health check endpoint."""
    return {
        "ok": True,
        "node": "describer",
        "service": "knowledge_expansion",
        "config_hash": CONFIG_HASH
    }


def extract_json_from_text(text: str) -> Optional[dict]:
    """
    Try to extract JSON specification from the model output.
    
    Args:
        text: Model output text
    
    Returns:
        Parsed JSON dict if found, else None
    """
    try:
        # Look for JSON block
        start = text.find("{")
        end = text.rfind("}") + 1
        
        if start >= 0 and end > start:
            json_str = text[start:end]
            return json.loads(json_str)
    except:
        pass
    
    return None


def strip_json_block(text: str) -> str:
    """Remove leading JSON specification from mixed content."""
    if not text:
        return ""
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        prefix = text[:start].strip()
        suffix = text[end + 1 :].strip()
        combined = " ".join(part for part in [prefix, suffix] if part)
        return combined.strip()
    return text.strip()


async def enforce_grounding(source_text: str, candidate: str) -> str:
    """Use LLM guard to strip hallucinations from description."""
    guard_messages = [
        {"role": "system", "content": HALLUCINATION_GUARD_PROMPT},
        {
            "role": "user",
            "content": (
                "User prompt:\n"
                f"{source_text.strip()}\n\n"
                "Candidate description:\n"
                f"{candidate.strip()}"
            ),
        },
    ]
    guard = await chat(guard_messages, temperature=0.0, max_tokens=220)
    guard_text = guard["text"].strip()
    if guard_text.upper().startswith("NO_SUPPORTED_CONTEXT"):
        return "No additional grounded context is available right now."
    return guard_text


@app.post("/describe", response_model=DescribeResponse)
async def describe(
    req: DescribeRequest,
    x_run_id: Optional[str] = Header(None),
    x_idempotency_key: Optional[str] = Header(None)
):
    """
    Generate description and context for a text prompt.
    
    Headers:
        X-Run-Id: Optional run ID for tracking
        X-Idempotency-Key: Optional idempotency key
    """
    run_id = req.run_id or x_run_id
    
    with Timer("describer", "describe") as timer:
        # Prepare messages
        msgs = [
            {"role": "system", "content": DESCR_SYS_RUNTIME},
            {"role": "user", "content": req.text},
        ]
        
        # Call vLLM
        out = await chat(msgs, temperature=0.2, max_tokens=300)
        
        raw_text = out["text"]
        
        # Try to extract JSON spec
        json_spec = extract_json_from_text(raw_text)
        summary_text = strip_json_block(raw_text)
        description_text = await enforce_grounding(req.text, summary_text)
        
        # Extract token usage from raw response
        raw = out.get("raw", {})
        usage = raw.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        
        # Record metrics
        record_tokens("describer", input_tokens, output_tokens, req.model)
    
    tokens = {
        "input": input_tokens,
        "output": output_tokens
    }
    
    # Save artifacts if run_id provided
    if run_id:
        save_run_artifacts(
            run_id=run_id,
            node_name="describer",
            input_data={"text": req.text},
            output_data={
                "description": description_text,
                "json_spec": json_spec,
                "tokens": tokens
            },
            timing={"latency_ms": timer.elapsed_ms},
            config_hash=CONFIG_HASH
        )
    
    return DescribeResponse(
        description=description_text,
        json_spec=json_spec,
        latency_ms=timer.elapsed_ms,
        tokens=tokens,
        config_hash=CONFIG_HASH
    )


@app.get("/")
def root():
    """Root endpoint with service information."""
    return {
        "service": "Describer Worker",
        "version": "2.0",
        "node": "jw3",
        "model": "Llama-3.2-3B-Instruct + Wikipedia LoRA",
        "endpoints": {
            "POST /describe": "Generate description and context",
            "GET /health": "Health check",
            "GET /metrics": "Prometheus metrics"
        },
        "config_hash": CONFIG_HASH
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")

