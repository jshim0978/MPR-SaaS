import asyncio, os, time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

CLEANER_URL = os.environ.get("CLEANER_URL", "http://129.254.202.252:8002")
DESCR_URL   = os.environ.get("DESCR_URL",   "http://129.254.202.253:8003")
PARA_URL    = os.environ.get("PARA_URL",    "http://129.254.202.129:8004")

app = FastAPI(title="MPR Orchestrator")

class InferIn(BaseModel):
    prompt: str

@app.get("/health")
def health():
    return {"ok": True, "cleaner": CLEANER_URL, "descr": DESCR_URL, "para": PARA_URL}

async def call_json(url: str, json: dict):
    t0 = time.perf_counter()
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(url, json=json)
        r.raise_for_status()
        return r.json(), (time.perf_counter() - t0) * 1000.0

@app.post("/infer")
async def infer(body: InferIn):
    prompt = body.prompt
    ill_formed = (len(prompt) < 30) or ("qwntum" in prompt or "computng" in prompt)

    if not ill_formed:
        return {
            "skipped": True,
            "final_prompt": prompt,
            "meta": {"reason": "heuristic_ok"},
            "latency_ms": {"total": 0.0}
        }

    t0 = time.perf_counter()
    clean_task = asyncio.create_task(call_json(f"{CLEANER_URL}/clean", {"text": prompt}))
    desc_task  = asyncio.create_task(call_json(f"{DESCR_URL}/describe", {"text": prompt}))
    para_task  = asyncio.create_task(call_json(f"{PARA_URL}/paraphrase", {"text": prompt}))
    try:
        (cleaned, clean_ms), (described, descr_ms), (paraphrased, para_ms) = await asyncio.gather(
            clean_task, desc_task, para_task
        )
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Worker error: {e}")

    final_prompt = cleaned.get("cleaned", prompt)
    desc = described.get("description", "")
    para = paraphrased.get("paraphrased", "")
    
    # Merge: paraphrase the cleaned version, then add description
    if para and para != final_prompt:
        final_prompt = para
    if desc:
        final_prompt = f"{final_prompt}\n\nContext: {desc}"

    total_ms = (time.perf_counter() - t0) * 1000.0
    return {
        "skipped": False,
        "cleaned": cleaned,
        "described": described,
        "paraphrased": paraphrased,
        "final_prompt": final_prompt,
        "latency_ms": {"cleaner": clean_ms, "descr": descr_ms, "para": para_ms, "total": total_ms}
    }
