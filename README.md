# MPR-SaaS: Multi-Prompt Refinement as a Service

**A cloud-native prompt refinement framework for reducing LLM hallucinations**

---

## 📊 Repository Structure

```
MPR-SaaS/
├── README.md                    ← This file
│
├── sbs29_baselines/             ← Baseline evaluation results (sbs29)
│   ├── README.md                   - Baseline results documentation
│   ├── SBS29_results.zip           - Complete results package (16 MB)
│   ├── baselines/                  - Baseline implementations
│   ├── datasets/                   - Evaluation datasets
│   ├── docs/                       - Replication guides
│   ├── graphs/                     - Visualizations
│   └── scripts/                    - Evaluation scripts
│
├── comparison/                  ← Comparison framework code (sbs29)
│   ├── baselines/                  - Framework implementations
│   ├── datasets/                   - Raw evaluation datasets
│   └── results_complete/           - Full evaluation results
│
├── orchestrator/                ← PRaaS orchestrator (jw1)
├── workers/                     ← Worker node code (jw2, jw3)
├── mpr/                         ← Core MPR library
├── config/                      ← Configuration files
└── prompts/                     ← Prompt templates
```

---

## 🎯 Quick Start

### For Baseline Evaluations (sbs29)

```bash
# View baseline results
cd sbs29_baselines/
unzip SBS29_results.zip
cat README.md
```

### For Running PRaaS Framework

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure
cp config/decoding.example.json config/decoding.json
# Edit config/decoding.json with your settings

# 3. Start orchestrator (jw1)
cd orchestrator/
python3 router.py

# 4. Start workers (jw2, jw3)
cd workers/
python3 cleaner.py  # jw2
python3 describer.py  # jw3
```

---

## 📊 Baseline Evaluation Results

**Completed on sbs29 (November 7-9, 2025)**

### Frameworks Evaluated:
- **Control**: Baseline (no refinement)
- **OPRO**: 1-iteration optimization
- **PromptAgent**: Strategic planning
- **PromptWizard**: 3-round mutation

### Datasets Used:
- **TruthfulQA**: 817 samples
- **GSM8K**: 1,319 samples
- **AmbigQA**: 2,002 samples
- **HaluEval**: 1,000 samples (sampled with seed=42)

### Performance Summary (per sample average):

| Framework | Latency (s) | Tokens | vs Control |
|-----------|-------------|--------|------------|
| Control | 17.0 | 641 | 1.00× |
| OPRO | 21.3 | 916 | 1.25× slower |
| PromptAgent | 26.7 | 1,100 | 1.57× slower |
| PromptWizard | 38.6 | 1,612 | 2.27× slower |

**See `sbs29_baselines/` for complete results and replication guides.**

---

## 🔧 Configuration

### Model Configuration (`config/decoding.json`)

```json
{
  "backbone_model": "meta-llama/Llama-3.2-3B-Instruct",
  "temperature": 0.2,
  "top_p": 0.9,
  "max_new_tokens": 512,
  "seed": 13
}
```

### Node Assignment

- **jw1**: Orchestrator (router, combiner, telemetry)
- **jw2**: Cleaner worker
- **jw3**: Describer worker
- **sbs29**: Baseline evaluations (trainer node)

---

## 📚 Documentation

### Essential Docs:
- **`sbs29_baselines/README.md`** - Baseline evaluation results
- **`sbs29_baselines/docs/REPLICATION_GUIDE.md`** - How to replicate evaluations
- **`sbs29_baselines/docs/DATA_COLLECTION_SPEC.md`** - Data format specification

### For Other Servers:
If you're running evaluations on jw1, jw2, jw3, or kcloud:
1. Create your own directory (e.g., `jw1_praas/`)
2. Follow the data format in `sbs29_baselines/docs/`
3. Use the same datasets from `sbs29_baselines/datasets/`
4. Commit your results to your directory (no conflicts!)

---

## 🎓 Citation

If using this codebase or baseline results:

```
MPR-SaaS: Multi-Prompt Refinement as a Service
Baseline evaluations conducted on sbs29 (November 2025)
Frameworks: Control, OPRO, PromptAgent, PromptWizard
Target Model: meta-llama/Llama-3.2-3B-Instruct
Datasets: TruthfulQA, GSM8K, AmbigQA, HaluEval
```

---

## 🔄 Contributing

### Adding Your Evaluation Results:

1. **Create your directory**:
   ```bash
   mkdir your_server_name/
   ```

2. **Add your results**:
   ```bash
   cp your_results.json your_server_name/
   git add your_server_name/
   ```

3. **Commit and push**:
   ```bash
   git commit -m "Add [your_server] evaluation results"
   git push origin main
   ```

### Directory Naming Convention:
- `sbs29_baselines/` - Baseline evaluations (sbs29)
- `jw1_praas/` - PRaaS evaluation (jw1)
- `jw2_worker/` - Worker node files (jw2)
- `jw3_worker/` - Worker node files (jw3)
- `kcloud_deployment/` - Deployment files (kcloud)

This ensures no conflicts between servers!

---

## ✅ Status

- ✅ **sbs29 baselines**: Complete (20,552 samples, 100% success)
- ⏳ **jw1 PRaaS**: In progress
- ⏳ **BBH, StrategyQA, CSQA**: To be evaluated
- ⏳ **EvoPrompt**: To be evaluated

---

## 📞 Questions?

For questions about:
- **Baseline results**: See `sbs29_baselines/README.md`
- **Replication**: See `sbs29_baselines/docs/REPLICATION_GUIDE.md`
- **Data format**: See `sbs29_baselines/docs/DATA_COLLECTION_SPEC.md`
- **Framework code**: See `comparison/` or respective worker directories

---

**Last Updated**: November 10, 2025  
**Repository**: https://github.com/jshim0978/MPR-SaaS  
**Rules used**: [JW-Global, MPR-Detected: yes]
