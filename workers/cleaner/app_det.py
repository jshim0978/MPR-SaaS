from fastapi import FastAPI
from pydantic import BaseModel
import os, httpx

app = FastAPI()

class Inp(BaseModel):
    text: str

SYSTEM_PROMPT = (
  "You are a proofreader. Return only the corrected user text. "
  "Fix typos and minor grammar. Do not add or remove facts. "
  "Do not explain. Output a single line of plain text."
)

async def call_vllm(messages, temperature=0.0, max_tokens=96):
    url = os.environ.get("OPENAI_BASE_URL","http://127.0.0.1:8001/v1") + "/chat/completions"
    model = os.environ.get("MODEL_NAME","meta-llama/Llama-3.2-3B-Instruct")
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(url, json={
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        })
        r.raise_for_status()
        data = r.json()
        return {"text": data["choices"][0]["message"]["content"]}

@app.post("/clean")
async def clean(inp: Inp):
    messages = [
      {"role":"system","content": SYSTEM_PROMPT},
      {"role":"user","content": inp.text.strip()}
    ]
    out = await call_vllm(messages, temperature=0.0, max_tokens=96)
    cleaned = out["text"].strip().replace("\n"," ")
    return {"cleaned": cleaned}

@app.get("/health")
async def health():
    return {"ok": True}
