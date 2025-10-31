# MPR-SaaS (Multi-stage Prompt Refinement as a Service)

**Cloud-native prompt refinement system using specialized fine-tuned LLMs**

> EACL 2025 workshop submission  
> Goal: Reduce casual hallucinations by ≥25% through systematic prompt improvement  
> Status: Models trained, deployment in progress

---

## 📊 Current Status (October 31, 2025)

### ✅ Completed
- **Training**: All 18 models trained (3B + 8B variants across 9 configurations)
- **Evaluation**: Comprehensive quality assessment on HHEM-style benchmarks
- **Model Selection**: 4 best models selected for production deployment
- **Code**: All framework code committed to GitHub
- **Documentation**: Deployment guides and model evaluation results

### 🚧 In Progress
- **Deployment**: Distributing selected models to production nodes
- **Testing**: End-to-end system validation

### 📋 Next Steps
1. Complete model distribution to jw2, jw3, kcloud
2. Start worker services (Cleaner on jw2, Describer on jw3)
3. Start orchestrator service (jw1)
4. Run end-to-end tests
5. Benchmark hallucination reduction on HHEM

---

## 🏗️ System Architecture

```
User Prompt → Orchestrator (jw1:8000)
              ↓
              Arbiter: Decide which specialists to invoke
              ↓
              Parallel Processing:
              ├─→ Cleaner (jw2:8002)
              │   • Fix typos and grammar
              │   • Model: 3B Grammar (JFLEG-trained)
              │
              └─→ Describer (jw3:8003)
                  • Add factual context
                  • Model: 3B Wikipedia-only (Quality: 8.8/10)
              ↓
              Merger: Combine improvements
              ↓
              Refined Prompt → Target LLM
```

---

## 🔬 Trained Models Summary

### Grammar Correction (Cleaner)
**Training Data**: JFLEG (6,012 samples)  
**Purpose**: Fix typos, grammar errors, improve clarity  
**Status**: ✅ Production-ready

| Model | Path | Deployment |
|-------|------|------------|
| 3B Grammar | `/models/llama32_3b_grammar_lora` | jw2 |
| 8B Grammar | `/models/llama31_8b_grammar_lora` | jw2 |

### Knowledge Expansion (Describer)

#### Wikipedia-only (SELECTED for production)
**Training Data**: Wikipedia Q&A (14,982 samples)  
**Purpose**: Add encyclopedic context, factual information  
**Quality**: 8.8/10 (best performance)  
**Status**: ✅ Production deployment

| Model | Path | Quality | Deployment |
|-------|------|---------|------------|
| 3B Wikipedia | `/models/llama32_3b_wikipedia_only_lora` | 8.8/10 | jw3 (primary) |
| 8B Wikipedia | `/models/llama31_8b_wikipedia_only_lora` | 8.8/10 | jw3 (alternate) |

**Why Wikipedia-only?**
- Most detailed responses (158-178 words avg)
- Excellent factual accuracy (17/20 high-quality)
- Encyclopedic, informative style (not conversational)

#### Wiki+Wikidata Combined (Backup)
**Training Data**: Wikipedia (14,982) + Wikidata (10,000) = 24,982 samples  
**Purpose**: Balanced detail with structured facts  
**Quality**: 8.2-8.5/10  
**Status**: ✅ Backup models on kcloud

| Model | Path | Quality | Deployment |
|-------|------|---------|------------|
| 3B Wiki+Wikidata | `/models/llama32_3b_knowledge_wiki_only_lora` | 8.2/10 | kcloud |
| 8B Wiki+Wikidata | `/models/llama31_8b_knowledge_wiki_only_lora` | 8.5/10 | kcloud |

#### ❌ Excluded Models

**Wikidata-only**: Too brief (2-3 words avg), lacks context, quality 4.0-4.3/10  
**KILT WOW**: Conversational dialogue style, too brief (89-90% shorter than base)  
**Combined Wiki+Wikidata+KILT**: Unwanted conversational tone from KILT contamination

### Paraphrasing (Reference)
**Training Data**: PAWS (48,976) + QQP (94,682) = 143,658 samples  
**Purpose**: Rephrase for clarity  
**Status**: Trained but not in current deployment (future work)

| Model | Path | Status |
|-------|------|--------|
| 3B Paraphrase | `/models/llama32_3b_paraphrase_lora` | Not deployed |
| 8B Paraphrase | `/models/llama31_8b_paraphrase_lora` | Not deployed |

### Individual Dataset Models (Evaluation Reference)
Additional models trained for comparison (not deployed):
- Wikidata-only (3B, 8B)
- KILT WOW-only (3B, 8B)
- PAWS-only (3B, 8B)
- QQP-only (3B, 8B)

**Total Models Trained**: 18 (9 configurations × 2 sizes)  
**Models in Production**: 4 (Grammar 3B+8B, Wikipedia 3B+8B)  
**Backup Models**: 2 (Wiki+Wikidata 3B+8B)

---

## 🎯 Production Deployment

### Node Configuration

| Node | IP | User | Role | Models Deployed | Port |
|------|-----|------|------|-----------------|------|
| **jw1** | 129.254.202.251 | etri | Orchestrator | None (coordination only) | 8000 |
| **jw2** | 129.254.202.252 | etri | Cleaner Worker | Grammar 3B + 8B | 8002 |
| **jw3** | 129.254.202.253 | etri | Describer Worker | Wikipedia 3B + 8B | 8003 |
| **kcloud** | 129.254.202.129 | root | Backup/Testing | Wiki+Wikidata 3B + 8B | N/A |

### Model Distribution Plan

```
Training Server (sbs29) → Production Nodes:

jw2 (Cleaner):
  ← llama32_3b_grammar_lora (~250MB)
  ← llama31_8b_grammar_lora (~500MB)

jw3 (Describer):
  ← llama32_3b_wikipedia_only_lora (~250MB)
  ← llama31_8b_wikipedia_only_lora (~500MB)

kcloud (Backup):
  ← llama32_3b_knowledge_wiki_only_lora (~250MB)
  ← llama31_8b_knowledge_wiki_only_lora (~500MB)
```

---

## 🚀 Deployment Instructions

**See**: [MANUAL_DEPLOYMENT.sh](MANUAL_DEPLOYMENT.sh) for complete step-by-step guide

### Quick Summary

1. **On each node** (jw1, jw2, jw3, kcloud):
   ```bash
   cd /home
   git clone https://github.com/jshim0978/MPR-SaaS.git temp
   rsync -av temp/ ./
   rm -rf temp
   pip3 install -r requirements.txt --user
   ```

2. **Transfer models from sbs29** (reverse rsync from each worker node):
   ```bash
   # On jw2:
   rsync -avz root@129.254.202.29:/home/models/llama32_3b_grammar_lora/ \
       /home/models/llama32_3b_grammar_lora/
   
   # On jw3:
   rsync -avz root@129.254.202.29:/home/models/llama32_3b_wikipedia_only_lora/ \
       /home/models/llama32_3b_wikipedia_only_lora/
   ```

3. **Download base models** (jw2, jw3):
   ```bash
   python3 -c "
   from transformers import AutoTokenizer, AutoModelForCausalLM
   AutoTokenizer.from_pretrained('meta-llama/Llama-3.2-3B-Instruct', cache_dir='/home/hf_cache')
   AutoModelForCausalLM.from_pretrained('meta-llama/Llama-3.2-3B-Instruct', cache_dir='/home/hf_cache')
   "
   ```

4. **Start services**:
   ```bash
   # jw2: cd /home/workers/cleaner && python3 app.py
   # jw3: cd /home/workers/descr && python3 app.py
   # jw1: cd /home/orchestrator && python3 app.py
   ```

5. **Test**:
   ```bash
   curl -X POST http://129.254.202.251:8000/refine \
     -H "Content-Type: application/json" \
     -d '{"prompt": "what is the captial of frane?", "run_id": "test-001"}'
   ```

---

## 📊 Key Evaluation Results

### Wikipedia-only Models (Production Choice)

**Test**: 20 factual questions from HHEM-style benchmark

| Metric | 3B Wikipedia | 8B Wikipedia |
|--------|-------------|-------------|
| **Quality Score** | 8.8/10 | 8.8/10 |
| **Accuracy** | 2.80/3.0 | 2.75/3.0 |
| **Completeness** | 2.95/3.0 | 2.95/3.0 |
| **Informativeness** | 2.05/3.0 | 2.05/3.0 |
| **Avg Response Length** | 158 words | 178 words |
| **High-quality Responses** | 17/20 | 17/20 |

**Why Wikipedia-only won**:
1. Most detailed and informative (vs. 95-129 words for Wiki+Wikidata)
2. Encyclopedic style (vs. conversational for KILT-trained models)
3. Excellent factual accuracy
4. Helpful for expanding prompts with context

See [docs/FINAL_MODEL_SELECTION.md](docs/FINAL_MODEL_SELECTION.md) for full evaluation.

---

## 📁 Repository Structure

```
/home/
├── README.md                  # This file
├── MANUAL_DEPLOYMENT.sh       # Step-by-step deployment guide
├── requirements.txt           # Python dependencies
│
├── orchestrator/             # Orchestrator service (jw1)
│   ├── app.py               # Main orchestration logic
│   └── app_det.py           # Deterministic variant
│
├── workers/                 # Worker services
│   ├── cleaner/            # Grammar/typo correction (jw2)
│   │   └── app.py
│   └── descr/              # Knowledge expansion (jw3)
│       └── app.py
│
├── mpr/                     # Core framework
│   ├── common/             # Shared utilities
│   └── telemetry/          # Prometheus metrics
│
├── prompts/                # System prompts
│   ├── typo.md            # Cleaner prompts
│   ├── keyword.md         # Keyword disambiguation
│   └── descr.md           # Describer prompts
│
├── config/                 # Configuration
│   └── decoding.json      # Model decoding params
│
├── configs/                # Training configs (reference)
│   ├── grammar/
│   └── knowledge/
│
├── scripts/
│   ├── deployment/        # Deployment automation
│   ├── training/          # Training scripts
│   └── dataset_prep/      # Dataset preparation
│
└── docs/
    └── FINAL_MODEL_SELECTION.md  # Model evaluation results
```

---

## 🔧 Configuration

### Fixed-Model Policy

- **Backbone (3B)**: `meta-llama/Llama-3.2-3B-Instruct`
- **Backbone (8B)**: `meta-llama/Llama-3.1-8B-Instruct`
- **Adapters**: LoRA (rank=8, alpha=16)
- **Decoding**: Loaded from `config/decoding.json`

### Environment Variables

```bash
# Required for inference:
export HF_HOME="/home/hf_cache"
export TRANSFORMERS_CACHE="/home/hf_cache"

# Optional for training:
export WANDB_API_KEY="your_key_here"
export WANDB_PROJECT="mpr-saas"
```

---

## 📊 API Reference

### Orchestrator (jw1:8000)

**POST** `/refine`
```json
{
  "prompt": "what is the captial of frane?",
  "run_id": "test-001",
  "idempotency_key": "optional-key"
}
```

**Response**:
```json
{
  "refined_prompt": "What is the capital of France? France is a country in Western Europe...",
  "cleaner_output": "what is the capital of France?",
  "describer_output": "France is a country in Western Europe. Its capital is Paris...",
  "latency_ms": 150,
  "run_id": "test-001"
}
```

**GET** `/health` - Returns `{"status": "ok"}`

### Workers

**GET** `/health` - Health check (jw2:8002, jw3:8003)

---

## 📈 Research Objectives

- **Hallucination Reduction**: ≥25% on HHEM benchmark
- **Utility Preservation**: ≤3% degradation
- **Latency**: <200ms p95 for refinement
- **Cost**: <$0.01 per refinement (4o-equivalent)

---

## 🔐 Security

- **No hardcoded credentials**: All secrets via environment variables
- **API keys**: Set `WANDB_API_KEY`, `HF_TOKEN` in `.env` (gitignored)
- **SSH**: Required for inter-node communication

---

## 📝 Training Data Summary

| Task | Datasets | Samples | Status |
|------|----------|---------|--------|
| **Grammar** | JFLEG | 6,012 | ✅ Deployed |
| **Knowledge (Production)** | Wikipedia-only | 14,982 | ✅ Deployed |
| **Knowledge (Backup)** | Wikipedia + Wikidata | 24,982 | ✅ Backup |
| **Paraphrasing** | PAWS + QQP | 143,658 | ✅ Trained (not deployed) |

**Key Decision**: Excluded KILT WOW (10,000 dialogue samples) from production due to unwanted conversational style.

---

## 🙏 Acknowledgments

- **Training Framework**: LLaMA Factory
- **Base Models**: Meta's Llama 3.2 (3B) and Llama 3.1 (8B)
- **Datasets**: JFLEG, Wikipedia, Wikidata, PAWS, QQP

---

## 📞 More Information

- **Deployment Guide**: [MANUAL_DEPLOYMENT.sh](MANUAL_DEPLOYMENT.sh)
- **Model Selection**: [docs/FINAL_MODEL_SELECTION.md](docs/FINAL_MODEL_SELECTION.md)
- **Architecture**: [.cursor/rules/eacl-manuscript-rules.mdc](.cursor/rules/eacl-manuscript-rules.mdc)

---

**Repository**: https://github.com/jshim0978/MPR-SaaS  
**Last Updated**: October 31, 2025  
**Status**: ✅ Training complete, 🚧 Deployment in progress
