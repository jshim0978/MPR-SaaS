# Comparison Methods Implementation Plan

**Based on**: EACL Manuscript - PRaaS comparison requirements  
**Goal**: Implement SOTA comparison frameworks for fair, budget-matched evaluation

---

## 📋 Methods from Manuscript

### **Primary Comparisons** (Global Prompt Optimizers)

| Method | Citation | Type | Budget-Matched Config | Status |
|--------|----------|------|----------------------|--------|
| **OPRO** | Yang et al., 2023 | Optimization by PROmpting | 1-iteration | 🔍 Research |
| **PromptBreeder** | Fernando et al., 2023 | Evolutionary optimization | 8×2 (8 candidates, 2 iterations) | 🔍 Research |
| **PromptAgent** | Wang et al., 2024b | Strategic planning | 1-pass | 🔍 Research |
| **ProTeGi** | Ramnath et al., 2023 | Textual gradients | 1-pass (header only) | 🔍 Research |

### **Input-Side Methods**

| Method | Citation | Type | Purpose | Status |
|--------|----------|------|---------|--------|
| **ADO** | Lin et al., 2025 | Adaptive data optimization | Format normalization | 🔍 Research |

### **Hallucination Detection/Verification**

| Method | Citation | Type | Purpose | Status |
|--------|----------|------|---------|--------|
| **SelfCheckGPT** | Manakul et al., 2023 | Self-consistency checking | Hallucination detection | 🔍 Research |
| **CoVe** | Dhuliawala et al., 2023 | Chain-of-Verification | Factuality verification | 🔍 Research |

### **Our Simple Baselines** (Already Implemented ✅)

| Method | Type | Status |
|--------|------|--------|
| Control | No refinement | ✅ Done |
| Template | Simple wrapper | ✅ Done |
| CoT | Chain-of-thought | ✅ Done |
| GPT-4 Refine | Commercial LLM | ✅ Done |
| Claude Refine | Commercial LLM | ✅ Done |
| MPR-SaaS | Our system | ✅ Done |

---

## 🎯 Implementation Strategy

### Phase 1: Research & Repository Discovery (Today)
1. Find official GitHub repositories for each method
2. Review implementation requirements (dependencies, models, APIs)
3. Identify budget-matched configurations
4. Document integration strategy

### Phase 2: Core Framework Integration (Days 1-2)
1. **OPRO (1-iter)**: Highest priority, referenced multiple times in manuscript
2. **PromptBreeder (8×2)**: Evolutionary baseline
3. **PromptAgent (1-pass)**: Strategic planning baseline
4. **ADO (format-only)**: Input normalization baseline

### Phase 3: Hallucination Probes (Days 2-3)
1. **SelfCheckGPT**: Self-consistency detection
2. **CoVe**: Chain-of-Verification
3. **HHEM scoring**: Primary metric (Vectara)
4. **Auxiliary probes**: QAGS/Q2, FActScore

### Phase 4: Evaluation Datasets (Day 3)
1. TruthfulQA (hallucination/faithfulness)
2. MT-Bench, IFEval (instruction following)
3. GSM8K, StrategyQA, CSQA, BBH (reasoning)
4. AmbigQA, ELI5 (ambiguity/underspec)
5. JFLEG, BEA (grammar/noise)

### Phase 5: Budget-Matched Experiments (Days 4-5)
1. Run all methods on common benchmark
2. Ensure token budget matching
3. Measure HHEM, cost, latency, utility
4. Generate comparison tables

---

## 📊 Expected Comparison Table (Table 2 from Manuscript)

| Method | HHEM ↓ | Cost ↑ | Latency ↑ | Utility ↓ |
|--------|--------|--------|-----------|-----------|
| Original (unrefined) | 0.42 | baseline | 0ms | 1.00 |
| OPRO (1-iter) | ? | HIGH | 500ms+ | ? |
| PromptBreeder (8×2) | ? | VERY HIGH | 1000ms+ | ? |
| PromptAgent (1-pass) | ? | HIGH | 500ms+ | ? |
| ADO (format-only) | 0.40 | LOW | 10ms | 0.99 |
| **MPR-SaaS (3B)** | **0.30** | **LOW** | **180ms** | **0.98** |
| **MPR-SaaS (8B)** | **0.28** | **LOW** | **200ms** | **0.98** |
| MPR-SaaS + ADO | 0.29 | LOW | 190ms | 0.98 |
| MPR-SaaS + OPRO (header) | 0.27 | MED | 250ms | 0.98 |

**Target Claims**:
- ✅ ≥25% HHEM reduction vs Original
- ✅ ≤3% utility drop
- ✅ Competitive with/better than global optimizers
- ✅ Lower cost and latency than iterative methods

---

## 🔍 Repository Research Status

### 1. OPRO (Yang et al., 2023)
- **Paper**: "Large Language Models as Optimizers"
- **Expected repo**: `google-deepmind/opro`
- **Key feature**: LLM generates optimization instructions
- **Budget config**: 1 iteration (vs default multiple)

### 2. PromptBreeder (Fernando et al., 2023)
- **Paper**: "Promptbreeder: Self-Referential Self-Improvement Via Prompt Evolution"
- **Expected repo**: `google-deepmind/evolutionary_prompting` or similar
- **Key feature**: Evolutionary algorithm for prompt optimization
- **Budget config**: 8 candidates × 2 iterations

### 3. PromptAgent (Wang et al., 2024b)
- **Paper**: Likely "Strategic Prompt Optimization"
- **Expected repo**: TBD (need to search)
- **Key feature**: Multi-agent strategic planning
- **Budget config**: 1-pass execution

### 4. ProTeGi (Ramnath et al., 2023)
- **Paper**: Likely "Textual Gradients for Prompt Optimization"
- **Expected repo**: TBD
- **Key feature**: Gradient-based prompt search
- **Budget config**: 1-pass, header only

### 5. ADO (Lin et al., 2025)
- **Paper**: "Adaptive Data Optimization" (very recent)
- **Expected repo**: TBD
- **Key feature**: Pre-inference format normalization
- **Budget config**: Format-only (no content changes)

### 6. SelfCheckGPT (Manakul et al., 2023)
- **Paper**: "SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection"
- **Known repo**: `potsawee/selfcheckgpt`
- **Key feature**: Self-consistency via sampling
- **Use**: Detection baseline, not refinement

### 7. CoVe (Dhuliawala et al., 2023)
- **Paper**: "Chain-of-Verification Reduces Hallucination in Large Language Models"
- **Expected repo**: Meta Research or similar
- **Key feature**: Generate → Verify → Revise
- **Use**: Verification baseline

---

## 🏗️ Integration Architecture

```
/home/comparison/
├── frameworks/                    # NEW: SOTA method implementations
│   ├── opro/
│   │   ├── adapter.py            # StandardizedMethod interface
│   │   ├── opro_1iter.py         # 1-iteration implementation
│   │   └── requirements.txt
│   ├── promptbreeder/
│   │   ├── adapter.py
│   │   ├── evolutionary_8x2.py   # 8×2 budget config
│   │   └── requirements.txt
│   ├── promptagent/
│   │   ├── adapter.py
│   │   ├── strategic_1pass.py
│   │   └── requirements.txt
│   ├── ado/
│   │   ├── adapter.py
│   │   ├── format_normalizer.py
│   │   └── requirements.txt
│   ├── selfcheckgpt/
│   │   ├── adapter.py
│   │   ├── detector.py
│   │   └── requirements.txt
│   └── cove/
│       ├── adapter.py
│       ├── verifier.py
│       └── requirements.txt
├── baselines/                     # EXISTING: Simple baselines
│   ├── control.py                ✅
│   ├── template.py               ✅
│   ├── cot.py                    ✅
│   ├── gpt4_refine.py            ✅
│   ├── claude_refine.py          ✅
│   └── mpr_saas.py               ✅
├── eval_harness/
│   ├── runner.py                 # Update to include SOTA methods
│   ├── metrics.py                # HHEM, QAGS, FActScore, etc.
│   ├── judge.py                  # GPT-5 two-sample protocol
│   └── cost_calc.py              ✅
├── datasets/
│   ├── truthfulqa.py             # Download TruthfulQA
│   ├── ifeval.py                 # Download IFEval
│   ├── gsm8k.py                  # Download GSM8K
│   └── ... (other datasets)
└── results/
    ├── comparison_table_2.csv    # Main results table
    └── budget_matched_experiments.json
```

---

## 📝 Standardized Interface

All comparison methods will implement:

```python
class StandardizedMethod:
    def refine(self, prompt: str) -> Dict:
        """
        Returns:
            refined_prompt: str
            latency_ms: float
            tokens_used: int
            metadata: Dict
        """
        pass
    
    def get_cost(self, tokens_used: int) -> float:
        """Calculate cost given token usage"""
        pass
    
    def __str__(self) -> str:
        """Method name for reporting"""
        pass
```

---

## 🎯 Success Criteria

1. ✅ All 7 SOTA methods implemented and runnable
2. ✅ Budget-matched configurations verified
3. ✅ Common evaluation harness for all methods
4. ✅ HHEM scoring working
5. ✅ Comparison table generated
6. ✅ Statistical significance tests run
7. ✅ MPR-SaaS shows ≥25% HHEM reduction
8. ✅ MPR-SaaS competitive with/better than global optimizers
9. ✅ Cost and latency advantages demonstrated

---

## 📦 Deliverables

1. **Code**: All 7 SOTA method adapters
2. **Data**: All evaluation datasets downloaded and prepared
3. **Results**: Comparison table (Table 2) with all methods
4. **Analysis**: Statistical tests, effect sizes, CIs
5. **Report**: Comprehensive comparison report
6. **LaTeX**: Tables ready for manuscript insertion

---

**Next Step**: Research GitHub repositories for each method and document integration requirements.

