# Research Findings: SelfCheckGPT and CoVe

**Research Date**: November 3, 2025  
**Researcher**: Training Server (SBS29)

---

## ✅ SelfCheckGPT

### Paper Information
- **Title**: "SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection for Generative Large Language Models"
- **Authors**: Manakul et al., 2023
- **arXiv**: https://arxiv.org/abs/2303.08896
- **GitHub**: https://github.com/potsawee/selfcheckgpt ✅ **FOUND**

### Key Methodology
1. **Zero-resource**: No external knowledge base needed
2. **Black-box**: Works with any generative LLM
3. **Self-consistency**: Generate multiple responses via sampling
4. **Detection**: Inconsistent facts across responses = hallucination

### Implementation Approach
- **Type**: Hallucination Detector (not a refiner)
- **Process**: 
  1. Generate N responses (temperature=1.0 for diversity)
  2. Compare responses for consistency
  3. Score: High variance = likely hallucination
- **Variants**:
  - SelfCheck-BERTScore (sentence-level)
  - SelfCheck-NLI (entailment-based)
  - SelfCheck-Prompt (LLM-based)

### Our Implementation
- **File**: `frameworks/selfcheckgpt/detector.py`
- **Approach**: Simplified consistency check
- **Samples**: 3 generations (configurable)
- **Output**: Hallucination score (0-1)
- **Integration**: Uses StandardizedMethod interface

---

## ✅ CoVe (Chain-of-Verification)

### Paper Information
- **Title**: "Chain-of-Verification Reduces Hallucination in Large Language Models"
- **Authors**: Dhuliawala et al., 2023
- **arXiv**: https://arxiv.org/abs/2309.11495
- **Institution**: Meta AI Research
- **GitHub**: No official repo found ❌

### Key Methodology
1. **Generate**: Baseline response to query
2. **Plan**: Generate verification questions
3. **Execute**: Answer verification questions independently
4. **Verify**: Check consistency between baseline and verifications
5. **Revise**: Generate final response incorporating verifications

### Four Variants (from paper)
1. **Joint**: All steps in one prompt
2. **2-Step**: Plan→Execute separately
3. **Factored**: Execute questions independently
4. **Factor+Revise**: Execute independently, then revise

### Implementation Approach
- **Type**: Verification-based Refiner
- **Process**:
  1. Generate baseline response
  2. Generate 2-3 verification questions
  3. Answer each question independently
  4. Synthesize final verified response
- **Variant**: Factor+Revise (most effective from paper)

### Our Implementation
- **File**: `frameworks/cove/verifier.py`
- **Approach**: Simplified 4-step pipeline
- **Verifications**: 2-3 questions per prompt
- **Output**: Verified refined response
- **Integration**: Uses StandardizedMethod interface

---

## 📊 Comparison: SelfCheckGPT vs CoVe

| Feature | SelfCheckGPT | CoVe |
|---------|--------------|------|
| **Purpose** | Detection | Refinement |
| **Approach** | Self-consistency | Verification loop |
| **Output** | Hallucination score | Refined response |
| **Steps** | 1 (parallel sampling) | 4 (sequential) |
| **Cost** | ~3× single generation | ~4-5× single generation |
| **Latency** | ~1-2s (parallel) | ~2-4s (sequential) |
| **Best for** | Detecting hallucinations | Reducing hallucinations |

---

## 🎯 Integration into MPR-SaaS Framework

### Use Cases

#### SelfCheckGPT
- **Post-generation check**: Detect if output contains hallucinations
- **Confidence scoring**: Add hallucination risk to responses
- **Filtering**: Flag high-risk outputs for human review
- **Comparison**: Benchmark detection vs our refinement approach

#### CoVe
- **Active refinement**: Improve prompts before target LLM
- **Verification layer**: Add verification step to MPR-SaaS
- **Fallback mechanism**: Use when Arbiter detects high uncertainty
- **Comparison**: Budget-matched refinement baseline

### Position in Comparison Framework

Both methods complement MPR-SaaS:
- **SelfCheckGPT**: Detection baseline (shows we reduce hallucinations)
- **CoVe**: Verification baseline (shows our approach is cost-effective)
- **MPR-SaaS**: Pre-inference refinement (faster, cheaper, preventive)

---

## 📝 Implementation Status

### SelfCheckGPT ✅
- [x] Research completed
- [x] Paper methodology understood
- [x] Reference implementation created
- [x] Integrated with StandardizedMethod
- [x] Standalone test working
- [ ] Full benchmark evaluation

### CoVe ✅
- [x] Research completed
- [x] Paper methodology understood
- [x] Reference implementation created (Factor+Revise variant)
- [x] Integrated with StandardizedMethod
- [x] Standalone test working
- [ ] Full benchmark evaluation

---

## 🔍 Key Citations from Manuscript

From `/home/manuscript.txt`:

> "Hallucination and judges. We use Vectara's HHEM (Vectara, 2024a,b; Chung and Team, 2024) with auxiliary probes (TruthfulQA (Lin et al., 2022), QAGS/Q2 (Wang and Cho, 2020; Honovich et al., 2021), **SelfCheckGPT (Manakul et al., 2023)**, **CoVe (Dhuliawala et al., 2023)**, faithfulness in summarization (Maynez et al., 2020))."

Both methods are referenced as **auxiliary probes** for hallucination measurement.

---

## 💡 Recommendations

### For Experiments
1. **Use SelfCheckGPT** as detection baseline (shows problem exists)
2. **Use CoVe** as refinement baseline (shows our approach is better)
3. **Compare costs**: MPR-SaaS vs CoVe (we should be 4-5× cheaper)
4. **Compare latency**: MPR-SaaS parallel vs CoVe sequential

### For Paper
1. **Table 2**: Include both as comparison methods
2. **Section 5**: Show MPR-SaaS prevents hallucinations CoVe would detect
3. **Discussion**: Position as complementary (we refine, they verify)
4. **Ablation**: Test MPR-SaaS + CoVe hybrid

---

**Status**: Both methods researched and implemented ✅  
**Ready for**: Integration into full comparison framework  
**Next**: Add to evaluation harness and run experiments

