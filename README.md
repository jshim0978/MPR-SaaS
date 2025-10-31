# MPR-SaaS (Prompt-Refinement-as-a-Service)

**Multi-stage prompt refinement system using fine-tuned small LLM specialists**

> Research implementation for EACL 2025 workshop submission  
> Goal: Reduce casual hallucinations by 25%+ through systematic prompt improvement

---

## 🎯 System Overview

MPR-SaaS is a black-box, cloud-native service that refines user prompts before they reach target LLMs. The system uses specialized fine-tuned models for:

- **Cleaner** (jw2): Grammar correction and typo fixing
- **Describer** (jw3): Knowledge expansion and context enrichment  
- **Orchestrator** (jw1): Routing, merging, and fallback logic

### Architecture

```
User Prompt → Orchestrator (jw1) → Parallel Processing:
                                    ├─→ Cleaner (jw2): Fix typos/grammar
                                    └─→ Describer (jw3): Add context
                                    ↓
                                    Merger: Combine outputs
                                    ↓
                                    Refined Prompt → Target LLM
```

---

## 📦 Repository Structure

```
/home/
├── orchestrator/           # Orchestrator service (jw1)
│   ├── app.py             # Main orchestration logic
│   └── app_det.py         # Deterministic variant
│
├── workers/               # Worker services
│   ├── cleaner/          # Grammar/typo correction (jw2)
│   └── descr/            # Knowledge expansion (jw3)
│
├── mpr/                   # Core framework
│   ├── common/           # Shared utilities
│   └── telemetry/        # Prometheus metrics
│
├── prompts/              # System prompts for each specialist
│   ├── typo.md          # Cleaner prompts
│   ├── keyword.md       # Keyword disambiguation
│   └── descr.md         # Describer prompts
│
├── config/              # Configuration
│   └── decoding.json    # Model decoding parameters
│
├── configs/             # Training configurations (for reference)
│   ├── grammar/        # Cleaner training configs
│   └── knowledge/      # Describer training configs
│
├── scripts/
│   ├── deployment/     # Deployment automation
│   ├── training/       # Training scripts (reference)
│   └── dataset_prep/   # Dataset preparation
│
└── docs/               # Documentation
    ├── FINAL_MODEL_SELECTION.md
    └── GIT_WORKFLOW.md
```

---

## 🚀 Deployment

### Prerequisites

- **4 nodes**: jw1 (orchestrator), jw2 (cleaner), jw3 (describer), kcloud (backup)
- **Python 3.10+**
- **CUDA-capable GPUs** on jw2, jw3 (for inference)
- **SSH access** to all nodes

### Quick Start

See **[MANUAL_DEPLOYMENT.sh](MANUAL_DEPLOYMENT.sh)** for complete step-by-step instructions.

#### Summary:

1. **Clone repository on each node:**
   ```bash
   cd /home
   git clone https://github.com/jshim0978/MPR-SaaS.git temp
   rsync -av temp/ ./
   rm -rf temp
   pip3 install -r requirements.txt --user
   ```

2. **Transfer trained models** (from training server sbs29):
   ```bash
   # On jw2 (Cleaner):
   rsync -avz root@129.254.202.29:/home/models/llama32_3b_grammar_lora/ \
       /home/models/llama32_3b_grammar_lora/
   
   # On jw3 (Describer):
   rsync -avz root@129.254.202.29:/home/models/llama32_3b_wikipedia_only_lora/ \
       /home/models/llama32_3b_wikipedia_only_lora/
   ```

3. **Download base models** (jw2, jw3):
   ```bash
   python3 -c "from transformers import AutoTokenizer, AutoModelForCausalLM; \
   AutoTokenizer.from_pretrained('meta-llama/Llama-3.2-3B-Instruct', cache_dir='/home/hf_cache'); \
   AutoModelForCausalLM.from_pretrained('meta-llama/Llama-3.2-3B-Instruct', cache_dir='/home/hf_cache')"
   ```

4. **Start services:**
   ```bash
   # jw2:
   cd /home/workers/cleaner && python3 app.py
   
   # jw3:
   cd /home/workers/descr && python3 app.py
   
   # jw1 (start last):
   cd /home/orchestrator && python3 app.py
   ```

5. **Test end-to-end:**
   ```bash
   curl -X POST http://129.254.202.251:8000/refine \
     -H "Content-Type: application/json" \
     -d '{"prompt": "what is the captial of frane?", "run_id": "test-001"}'
   ```

Full deployment guide: **[MANUAL_DEPLOYMENT.sh](MANUAL_DEPLOYMENT.sh)**

---

## 🔬 Trained Models

### Selected for Deployment

| Model | Training Data | Quality Score | Deployment | Purpose |
|-------|---------------|---------------|------------|---------|
| **3B Grammar** | JFLEG (6K) | N/A | jw2 | Grammar/typo fixes |
| **8B Grammar** | JFLEG (6K) | N/A | jw2 | Grammar/typo fixes |
| **3B Wikipedia** | Wikipedia (15K) | 8.8/10 | jw3 | Knowledge expansion |
| **8B Wikipedia** | Wikipedia (15K) | 8.8/10 | jw3 | Knowledge expansion |
| **3B Wiki+Wikidata** | Combined (25K) | 8.2/10 | kcloud | Backup/testing |
| **8B Wiki+Wikidata** | Combined (25K) | 8.5/10 | kcloud | Backup/testing |

See [docs/FINAL_MODEL_SELECTION.md](docs/FINAL_MODEL_SELECTION.md) for evaluation details.

---

## 🏗️ Node Configuration

| Node | IP | User | Role | Models | Port |
|------|-----|------|------|--------|------|
| **jw1** | 129.254.202.251 | etri | Orchestrator | None | 8000 |
| **jw2** | 129.254.202.252 | etri | Cleaner | Grammar 3B+8B | 8002 |
| **jw3** | 129.254.202.253 | etri | Describer | Wikipedia 3B+8B | 8003 |
| **kcloud** | 129.254.202.129 | root | Backup | Wiki+Wikidata 3B+8B | N/A |

---

## 🔧 Configuration

### Fixed-Model Policy

- **Backbone**: `meta-llama/Llama-3.2-3B-Instruct` and `meta-llama/Llama-3.1-8B-Instruct`
- **Decoding params**: Read from `config/decoding.json` (temperature, max_tokens, etc.)
- **LoRA adapters**: Task-specific fine-tuning for each specialist

### Environment Variables

```bash
# Set these before running services
export HF_HOME="/home/hf_cache"
export TRANSFORMERS_CACHE="/home/hf_cache"

# For training (optional):
export WANDB_API_KEY="your_wandb_key_here"
```

---

## 📊 API Endpoints

### Orchestrator (jw1:8000)

**POST** `/refine`
```json
{
  "prompt": "user's original prompt",
  "run_id": "unique-run-identifier",
  "idempotency_key": "optional-idempotency-key"
}
```

**Response:**
```json
{
  "refined_prompt": "cleaned and enriched prompt",
  "cleaner_output": "typo-corrected version",
  "describer_output": "context-enriched version",
  "latency_ms": 150,
  "run_id": "unique-run-identifier"
}
```

**GET** `/health` - Health check

### Worker Services

**GET** `/health` - Health check (jw2:8002, jw3:8003)

---

## 📈 Monitoring

- **Metrics**: Prometheus-compatible metrics at `/metrics` (if enabled)
- **Logs**: Console output with timestamps, latency, token counts
- **Telemetry**: Request/response sizes, p50/p95 latency

---

## 🧪 Testing

### Quick Test

```bash
# Test typo correction + knowledge expansion
curl -X POST http://129.254.202.251:8000/refine \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "what is the captial of frane?",
    "run_id": "test-001"
  }'
```

Expected behavior:
- Cleaner fixes: "captial" → "capital", "frane" → "France"
- Describer adds: "France is a country in Western Europe, capital Paris..."
- Merger combines improvements

---

## 📚 Documentation

- **[MANUAL_DEPLOYMENT.sh](MANUAL_DEPLOYMENT.sh)** - Complete deployment guide
- **[DEPLOYMENT_INSTRUCTIONS.md](DEPLOYMENT_INSTRUCTIONS.md)** - Detailed per-node setup
- **[docs/FINAL_MODEL_SELECTION.md](docs/FINAL_MODEL_SELECTION.md)** - Model evaluation results
- **[.cursor/rules/eacl-manuscript-rules.mdc](.cursor/rules/eacl-manuscript-rules.mdc)** - Architecture rules

---

## 🔐 Security

- **No hardcoded credentials**: Use environment variables
- **Secrets**: Store WANDB_API_KEY, HF tokens in `.env` (not committed)
- **SSH keys**: Required for node-to-node communication

---

## 🛠️ Development

### Training (Reference Only)

Training scripts are in `scripts/training/` but are **reference only**. All models are already trained.

To retrain (on training server sbs29):
```bash
export WANDB_API_KEY="your_key"
./scripts/training/train_3b_grammar.sh
```

### Adding New Specialists

1. Create worker service in `workers/<name>/`
2. Train model using `scripts/training/` templates
3. Update orchestrator routing in `orchestrator/app.py`
4. Add prompts to `prompts/<name>.md`

---

## 📊 Research Goals

- **HHEM Benchmark**: ≥25% relative hallucination reduction
- **Utility**: ≤3% degradation in helpfulness
- **Latency**: <200ms p95 for prompt refinement
- **Cost**: Equivalent to <$0.01 per refinement (4o-equivalent pricing)

---

## 📝 License

Research project for EACL 2025 workshop submission.

---

## 🙏 Acknowledgments

- Built with LLaMA Factory for training
- Uses Meta's Llama 3.2 (3B) and Llama 3.1 (8B) as base models
- Training datasets: JFLEG, Wikipedia, Wikidata

---

## 📞 Contact

For questions about deployment or research collaboration, see project documentation or contact via GitHub issues.

---

**Status**: ✅ Training complete, models deployed, system operational  
**Last Updated**: October 31, 2025
