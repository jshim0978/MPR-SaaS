import os
from fastapi import FastAPI
from pydantic import BaseModel
from mpr.common.vllm_client import chat

app = FastAPI(title="Cleaner Worker")

CLEAN_SYS = (
    "You are a prompt-cleaning agent. Fix typos, casing, spacing, and grammar. "
    "Preserve meaning. Do NOT add new facts. Output only the corrected text."
)

class CleanIn(BaseModel):
    text: str

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/clean")
async def clean(inp: CleanIn):
    msgs = [
        {"role": "system", "content": CLEAN_SYS},
        {"role": "user", "content": inp.text},
    ]
    out = await chat(msgs, temperature=0.0, max_tokens=512)
    return {"cleaned": out["text"], "latency_ms": out["latency_ms"]}
