# JFLEG Llama LoRA Comparison Project

This repository contains scripts for fine-tuning Llama models on the JFLEG (Japanese and English Grammatical Error Correction) dataset using LoRA for fair comparison.

## Project Structure

```
/home/
├── data/                           # Dataset files
│   ├── jfleg_all_corrections_train.jsonl    # Training data (4,809 samples)
│   ├── jfleg_all_corrections_eval.jsonl     # Evaluation data (601 samples)
│   └── jfleg_all_corrections_test.jsonl     # Test data (602 samples)
├── models/                         # Model outputs
│   ├── llama32_3b_lora/           # Fine-tuned Llama 3.2 3B LoRA
│   └── llama31_8b_lora/           # Fine-tuned Llama 3.1 8B LoRA
├── train_llama32_3b_lora.py       # Llama 3.2 3B LoRA training script
├── train_llama31_8b_lora.py       # Llama 3.1 8B LoRA training script
├── run_llama32_3b_lora_training.sh # Llama 3.2 3B LoRA training runner
├── run_llama31_8b_lora_training.sh # Llama 3.1 8B LoRA training runner
├── model_comparison.py             # Model comparison script
├── prepare_jfleg_dataset.py       # Dataset preparation script
└── archive_old_scripts/            # Old testing scripts
```

## Models

- **Llama 3.2 3B**: Fine-tuned using LoRA (Low-Rank Adaptation)
- **Llama 3.1 8B**: Fine-tuned using LoRA (Low-Rank Adaptation) for fair comparison

## Training Configuration

### Llama 3.2 3B (LoRA)
- **Method**: LoRA with r=16, alpha=32
- **Batch Size**: 4 per device
- **Learning Rate**: 2e-4
- **Epochs**: 3
- **Target Modules**: q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj

### Llama 3.1 8B (LoRA)
- **Method**: LoRA with r=16, alpha=32
- **Batch Size**: 4 per device (same as 3B for fair comparison)
- **Gradient Accumulation**: 8 steps
- **Learning Rate**: 2e-4
- **Epochs**: 3

## Usage

### Training Llama 3.2 3B LoRA
```bash
./run_llama32_3b_lora_training.sh
```

### Training Llama 3.1 8B LoRA
```bash
./run_llama31_8b_lora_training.sh
```

### Model Comparison
```bash
python3 model_comparison.py
```

## Monitoring

Training progress is logged to Weights & Biases:
- **Project**: jfleg-llama-lora-comparison
- **Dashboard**: https://wandb.ai/jshim0978/jfleg-llama-lora-comparison

## Dataset

The JFLEG dataset contains 1,503 original samples, each with 4 human corrections, expanded to 6,012 total examples:
- Training: 4,809 samples (using all corrections)
- Evaluation: 601 samples
- Test: 602 samples

This approach provides maximum training diversity by using all human-annotated corrections rather than selecting just one per original sentence.

Each sample contains a sentence with grammatical errors and its corrected version.
