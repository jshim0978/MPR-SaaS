import os, json, time
from fastapi import FastAPI
from pydantic import BaseModel
import httpx
from fastapi.responses import JSONResponse

OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "http://localhost:8001/v1")
MODEL = os.environ.get("MODEL_NAME", "meta-llama/Llama-3.2-3B-Instruct")

def j(x): return JSONResponse(content=x, media_type="application/json")

app = FastAPI()

class Inp(BaseModel):
    text: str

def load_prompt(text:str)->str:
    with open("prompts/descr.md", "r", encoding="utf-8") as f:
        tpl = f.read()
    return tpl.replace('{{INPUT}}', text)

async def call_openai(messages, decoding):
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": decoding.get("temperature", 0.2),
        "top_p": decoding.get("top_p", 0.9),
        "max_tokens": decoding.get("max_tokens", 512),
        "seed": decoding.get("seed", 42)
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(f"{OPENAI_BASE_URL}/chat/completions", json=payload)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()

@app.get("/health")
async def health():
    return {"ok": True}

@app.post("/describe")
async def describe(inp: Inp):
    with open("config/decoding.json") as f:
        decoding = json.load(f)
    prompt = load_prompt(inp.text)
    t0=time.time()
    out = await call_openai([{"role":"user","content":prompt}], decoding)
    dt=int((time.time()-t0)*1000)
    return j({"mode":"describe","output":out,"latency_ms":dt})
