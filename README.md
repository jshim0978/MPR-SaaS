# MPR-SaaS (minimal demo)
- jw2: Cleaner worker (typo/keyword) proxied to vLLM on jw2:8001
- jw3: Describer worker proxied to vLLM on jw3:8001
- jw1: Orchestrator calls both in parallel, merges result

See `requirements.txt`, `workers/*/app.py`, `orchestrator/app.py`.
