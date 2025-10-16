import os, asyncio, httpx, time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

CLEANER_URL = os.environ.get("CLEANER_URL", "http://129.254.202.252:9001")
DESCR_URL   = os.environ.get("DESCR_URL",   "http://129.254.202.253:9002")
TIMEOUT_S   = float(os.environ.get("ORCH_TIMEOUT", "60"))

app = FastAPI(title="MPR Orchestrator")

class InferIn(BaseModel):
    prompt: str

@app.get("/health")
def health():
    return {"ok": True, "cleaner": CLEANER_URL, "descr": DESCR_URL}

async def _post_json(url: str, payload: dict):
    async with httpx.AsyncClient(timeout=TIMEOUT_S) as client:
        r = await client.post(url, json=payload)
        r.raise_for_status()
        return r.json()

@app.post("/infer")
async def infer(inp: InferIn):
    t0 = time.perf_counter()
    # call both services in parallel
    clean_task = asyncio.create_task(_post_json(f"{CLEANER_URL}/clean", {"text": inp.prompt}))
    desc_task  = asyncio.create_task(_post_json(f"{DESCR_URL}/describe", {"text": inp.prompt}))
    try:
        cleaner, descr = await asyncio.gather(clean_task, desc_task)
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Worker error: {e}")

    cleaned = cleaner.get("cleaned", "").strip()
    desc    = descr.get("description", "").strip()

    final_prompt = cleaned
    if desc:
        # normalize bullets: ensure lines start with a dash
        lines = [ln if ln.lstrip().startswith(("-", "•", "*")) else f"- {ln.strip()}"
                 for ln in desc.splitlines() if ln.strip()]
        final_prompt = f"{cleaned}\n\nContext:\n" + "\n".join(lines)

    return {
        "final_prompt": final_prompt,
        "stages": {
            "cleaner_ms": cleaner.get("latency_ms", None),
            "descr_ms": descr.get("latency_ms", None),
            "orchestrator_ms": (time.perf_counter() - t0) * 1000.0,
            "note": "parallel calls to jw2/jw3"
        }
    }
