from fastapi import FastAPI
from pydantic import BaseModel
from mpr.common.vllm_client import chat

app = FastAPI(title="Paraphraser Worker")

PARA_SYS = (
    "You are a paraphrasing agent. Rephrase the input for clarity and naturalness. "
    "Preserve the original meaning and intent. Make it more fluent and readable. "
    "Output only the paraphrased text."
)

class ParaIn(BaseModel):
    text: str

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/paraphrase")
async def paraphrase(inp: ParaIn):
    msgs = [
        {"role": "system", "content": PARA_SYS},
        {"role": "user", "content": inp.text},
    ]
    out = await chat(msgs, temperature=0.3, max_tokens=512)
    return {"paraphrased": out["text"], "latency_ms": out["latency_ms"]}

