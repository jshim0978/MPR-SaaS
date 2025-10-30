# Model Distribution Manifest
# Generated: 2025-10-31
# Training Server: sbs29.etri.re.kr (129.254.184.194)

## Models Ready for Distribution

### Cleaner Agent (Grammar/Noise) → jw2 (129.254.202.252)
- **3B Default:**
  - Source: `/home/models/llama32_3b_grammar_lora/`
  - Target: `jw2:/home/models/llama32_3b_grammar_lora/`
  - Base: meta-llama/Llama-3.2-3B-Instruct
  - Training: JFLEG dataset
  
- **8B Appendix:**
  - Source: `/home/models/llama31_8b_grammar_lora/`
  - Target: `jw2:/home/models/llama31_8b_grammar_lora/`
  - Base: meta-llama/Llama-3.1-8B-Instruct
  - Training: JFLEG dataset

### Description Generator (Context) → jw3 (129.254.202.253)
- **3B Default:**
  - Source: `/home/models/llama32_3b_wikipedia_only_lora/`
  - Target: `jw3:/home/models/llama32_3b_wikipedia_only_lora/`
  - Base: meta-llama/Llama-3.2-3B-Instruct
  - Training: Wikipedia-only (14,982 samples)
  - Quality: 8.8/10 HHEM score
  
- **8B Appendix:**
  - Source: `/home/models/llama31_8b_wikipedia_only_lora/`
  - Target: `jw3:/home/models/llama31_8b_wikipedia_only_lora/`
  - Base: meta-llama/Llama-3.1-8B-Instruct
  - Training: Wikipedia-only (14,982 samples)
  - Quality: 8.8/10 HHEM score

### Paraphraser Agent (Clarity) → kcloud (129.254.202.129)
- **3B Default:**
  - Source: `/home/models/llama32_3b_paraphrase_lora/`
  - Target: `kcloud:/home/models/llama32_3b_paraphrase_lora/`
  - Base: meta-llama/Llama-3.2-3B-Instruct
  - Training: PAWS + QQP combined
  
- **8B Appendix:**
  - Source: `/home/models/llama31_8b_paraphrase_lora/`
  - Target: `kcloud:/home/models/llama31_8b_paraphrase_lora/`
  - Base: meta-llama/Llama-3.1-8B-Instruct
  - Training: PAWS + QQP combined

## Training Configuration
- LoRA rank: 16 (3B), 32 (8B)
- LoRA alpha: 32
- Learning rate: 1e-4 to 2e-4
- Epochs: 3
- Batch size: effective 256 via gradient accumulation
- Precision: bf16
- Optimizer: AdamW with cosine schedule

## Quality Benchmarks (from evaluation)
- Wikipedia-only models: 8.8/10 quality score, 17/20 high-quality responses
- Grammar models: Tested on JFLEG/BEA
- Paraphrase models: Tested on PAWS/MSRP

## Files to Transfer (per model)
- adapter_config.json
- adapter_model.safetensors (or .bin)
- special_tokens_map.json
- tokenizer_config.json
- tokenizer.json (if exists)

## Transfer Method
Command template:
```bash
rsync -avz --progress \
  /home/models/[model_name]/ \
  [user]@[node_ip]:/home/models/[model_name]/
```

## Verification
After each transfer, verify:
1. All adapter files present
2. File sizes match source
3. Can load adapter with PEFT library

## Status
- [ ] Cleaner models → jw2
- [ ] Describer models → jw3
- [ ] Paraphraser models → kcloud
- [ ] All checksums verified
- [ ] All nodes tested

---
**Deployment Date:** TBD
**Deployed By:** Training Server (sbs29)
**Next Step:** Framework implementation (Week 1 plan)

