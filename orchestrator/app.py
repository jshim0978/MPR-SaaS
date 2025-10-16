import os, json, time, asyncio
from typing import Dict, Any
from fastapi import FastAPI
from pydantic import BaseModel
import httpx
from fastapi.responses import JSONResponse

CLEANER_URL = os.environ.get("CLEANER_URL", "http://jw2:9001")
DESCR_URL   = os.environ.get("DESCR_URL", "http://jw3:9002")

def j(x): return JSONResponse(content=x, media_type="application/json")

app = FastAPI()

class InferIn(BaseModel):
    prompt: str

def ill_formed_score(s: str) -> float:
    bad = sum(s.count(x) for x in ["???",".."," plese "," teh "," idk "])
    return min(1.0, bad / 3.0)

async def post_json(url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(url, json=payload)
        r.raise_for_status()
        return r.json()

@app.get("/health")
async def health():
    return {"ok": True}

@app.post("/infer")
async def infer(inp: InferIn):
    t0 = time.time()
    score = ill_formed_score(inp.prompt)
    stages = []
    refined = inp.prompt

    if score < 0.2:
        stages.append({"skip_gate": True, "reason": "prompt seems clean"})
        return j({
            "run_id": f"run-{int(t0)}",
            "final_prompt": refined,
            "stages": stages,
            "latency_ms": int((time.time()-t0)*1000)
        })

    payload_clean_typo = {"text": inp.prompt, "mode":"typo"}
    payload_clean_kw   = {"text": inp.prompt, "mode":"keyword"}
    payload_descr      = {"text": inp.prompt}

    typo, keyword, descr = await asyncio.gather(
        post_json(f"{CLEANER_URL}/typo_fix", payload_clean_typo),
        post_json(f"{CLEANER_URL}/keyword_subst", payload_clean_kw),
        post_json(f"{DESCR_URL}/describe", payload_descr)
    )

    stages.append({"cleaner_typo_ms": typo["latency_ms"],
                   "cleaner_keyword_ms": keyword["latency_ms"],
                   "descr_ms": descr["latency_ms"]})

    refined = keyword["output"]
    refined_with_context = f"{refined}\n\nContext summary: {descr['output'][:400]}"

    return j({
        "run_id": f"run-{int(t0)}",
        "final_prompt": refined_with_context,
        "stages": stages,
        "latency_ms": int((time.time()-t0)*1000)
    })
