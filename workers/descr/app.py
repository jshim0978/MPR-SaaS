from fastapi import FastAPI
from pydantic import BaseModel
from mpr.common.vllm_client import chat

app = FastAPI(title="Describer Worker")

DESCR_SYS = (
    "You are a description-generating agent. Given a user query, add short, useful context: "
    "clarify ambiguous terms, list key entities or subtopics, and expand acronyms. "
    "Do NOT invent facts. Output 3-6 bullet points, concise."
)

class DescIn(BaseModel):
    text: str

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/describe")
async def describe(inp: DescIn):
    msgs = [
        {"role": "system", "content": DESCR_SYS},
        {"role": "user", "content": inp.text},
    ]
    out = await chat(msgs, temperature=0.2, max_tokens=300)
    return {"description": out["text"], "latency_ms": out["latency_ms"]}
