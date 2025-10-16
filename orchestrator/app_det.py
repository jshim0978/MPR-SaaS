from fastapi import FastAPI
from pydantic import BaseModel
import os, asyncio, httpx, time, re
from datetime import datetime
from pathlib import Path
import csv, subprocess, uuid

app = FastAPI()

class Req(BaseModel):
    prompt: str

TELEM_PATH = Path("runs/telemetry.csv")
TELEM_PATH.parent.mkdir(parents=True, exist_ok=True)

def git_rev():
    try:
        return subprocess.check_output(["git","rev-parse","--short","HEAD"], text=True).strip()
    except Exception:
        return "nogit"

def log_row(row: dict):
    new = not TELEM_PATH.exists()
    with TELEM_PATH.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=row.keys())
        if new: w.writeheader()
        w.writerow(row)

def is_well_formed(text: str) -> bool:
    t = text.strip()
    if len(t) >= 90 and (sum(not c.isalpha() and not c.isspace() for c in t)/max(1,len(t))) <= 0.2:
        if not re.search(r"(?:\\bplz\\b|\\bu\\b|\\bthx\\b|[\\w]{3}\\?\\?)", t, re.I):
            return True
    return False

@app.get("/health")
async def health():
    return {"ok": True}

@app.post("/infer")
async def infer(req: Req):
    req_id = uuid.uuid4().hex[:8]
    t0 = time.perf_counter()
    skip = is_well_formed(req.prompt)
    cleaner_text, descr_text = None, None
    lat_cleaner = lat_descr = 0.0

    async with httpx.AsyncClient(timeout=60) as client:
        if not skip:
            # cleaner
            c0 = time.perf_counter()
            cl = await client.post(os.environ.get("CLEANER_URL","http://127.0.0.1:9001") + "/clean",
                                   json={"text": req.prompt})
            cl.raise_for_status()
            cleaner_text = cl.json().get("cleaned","")
            lat_cleaner = (time.perf_counter()-c0)*1000
            # describer
            d0 = time.perf_counter()
            ds = await client.post(os.environ.get("DESCR_URL","http://127.0.0.1:9002") + "/descr",
                                   json={"text": req.prompt})
            ds.raise_for_status()
            descr_text = ds.json().get("description","")
            lat_descr = (time.perf_counter()-d0)*1000

    final_prompt = req.prompt if skip else f"{cleaner_text}\n{descr_text}"
    total_ms = (time.perf_counter()-t0)*1000

    row = dict(
      ts_iso=datetime.utcnow().isoformat(timespec="seconds"),
      req_id=req_id,
      input_len=len(req.prompt),
      skip=skip,
      cleaner_latency_ms=round(lat_cleaner,2),
      descr_latency_ms=round(lat_descr,2),
      total_ms=round(total_ms,2),
      cleaner_out_len=len(cleaner_text or ""),
      descr_out_len=len(descr_text or ""),
      final_len=len(final_prompt),
      jw2_model=os.environ.get("CLEANER_MODEL","meta-llama/Llama-3.2-3B-Instruct"),
      jw3_model=os.environ.get("DESCR_MODEL","meta-llama/Llama-3.2-3B-Instruct"),
      orchestrator_git_rev=git_rev(),
    )
    log_row(row)

    return {
        "req_id": req_id,
        "skipped": skip,
        "cleaned": cleaner_text,
        "described": descr_text,
        "final_prompt": final_prompt,
        "latency_ms": {
            "cleaner": round(lat_cleaner,2),
            "descr": round(lat_descr,2),
            "total": round(total_ms,2)
        }
    }
