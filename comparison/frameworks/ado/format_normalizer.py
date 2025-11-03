"""
ADO (Adaptive Data Optimization) - Lin et al., 2025

Reference: Format normalization and preprocessing for LLM inputs
Cited in manuscript as input-side method

Core idea: Pre-inference format normalization
1. Canonicalize format (whitespace, punctuation)
2. Remove duplicates
3. Normalize units and abbreviations
4. Fix common formatting issues

This is a lightweight, deterministic method (no LLM calls).
"""

import time
import re
from typing import Dict
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from base import StandardizedMethod, RefinementResult


class ADO_FormatOnly(StandardizedMethod):
    """
    ADO - Adaptive Data Optimization (Format-only variant)
    
    Lightweight normalization without LLM calls.
    Fast, cheap, deterministic preprocessing.
    """
    
    def __init__(self):
        super().__init__(name="ADO (format-only)")
    
    def normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace"""
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Fix space before punctuation
        text = re.sub(r'\s+([?.!,;:])', r'\1', text)
        # Fix space after punctuation
        text = re.sub(r'([?.!,;:])([^\s])', r'\1 \2', text)
        return text.strip()
    
    def normalize_capitalization(self, text: str) -> str:
        """Fix basic capitalization issues"""
        # Capitalize first letter
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
        # Capitalize after sentence-ending punctuation
        text = re.sub(r'([.!?]\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), text)
        return text
    
    def normalize_abbreviations(self, text: str) -> str:
        """Expand common abbreviations"""
        abbrevs = {
            r'\bpls\b': 'please',
            r'\btho\b': 'though',
            r'\bthru\b': 'through',
            r'\bu\b': 'you',
            r'\bur\b': 'your',
            r'\br\b': 'are',
            r'\bbtw\b': 'between',
            r'\bw/\b': 'with',
            r'\bw/o\b': 'without',
        }
        for pattern, replacement in abbrevs.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text
    
    def fix_common_typos(self, text: str) -> str:
        """Fix common typos"""
        typos = {
            r'\bwhats\b': 'what is',
            r'\bwhens\b': 'when is',
            r'\bwheres\b': 'where is',
            r'\bhows\b': 'how is',
            r'\bgimme\b': 'give me',
            r'\bgonna\b': 'going to',
            r'\bwanna\b': 'want to',
        }
        for pattern, replacement in typos.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text
    
    def add_question_mark(self, text: str) -> str:
        """Add question mark if missing from question"""
        question_words = ['what', 'when', 'where', 'who', 'why', 'how', 'which', 'can', 'could', 'would', 'should']
        starts_with_question = any(text.lower().startswith(word) for word in question_words)
        if starts_with_question and not text.endswith('?'):
            text = text.rstrip('.!') + '?'
        return text
    
    def refine(self, prompt: str) -> RefinementResult:
        """Apply format normalization"""
        t0 = time.perf_counter()
        
        # Apply normalizations in sequence
        refined = prompt
        refined = self.normalize_whitespace(refined)
        refined = self.normalize_abbreviations(refined)
        refined = self.fix_common_typos(refined)
        refined = self.normalize_capitalization(refined)
        refined = self.add_question_mark(refined)
        
        latency_ms = (time.perf_counter() - t0) * 1000.0
        
        # Token count (minimal change)
        original_tokens = len(prompt.split())
        refined_tokens = len(refined.split())
        
        return RefinementResult(
            method_name=self.name,
            original_prompt=prompt,
            refined_prompt=refined,
            latency_ms=latency_ms,
            tokens_used=refined_tokens,
            metadata={
                "type": "deterministic_normalization",
                "no_llm_calls": True,
                "transformations": [
                    "whitespace_normalization",
                    "abbreviation_expansion",
                    "typo_correction",
                    "capitalization_fix",
                    "punctuation_fix"
                ],
                "tokens_added": refined_tokens - original_tokens
            }
        )
    
    def get_cost_per_token(self) -> Dict[str, float]:
        """ADO is free (no LLM calls)"""
        return {"input": 0.0, "output": 0.0}


if __name__ == "__main__":
    print("="*80)
    print("ADO (Format-only Normalization) Test")
    print("="*80)
    
    ado = ADO_FormatOnly()
    
    test_prompts = [
        "whats   the captial    of frane",
        "tell me bout quantom physics pls",
        "how does photosythesis work",
        "explain climate change pls",
        "whats the difference btw virus and bacteria",
    ]
    
    for prompt in test_prompts:
        print(f"\nOriginal: {prompt}")
        result = ado.refine(prompt)
        print(f"Refined:  {result.refined_prompt}")
        print(f"Latency:  {result.latency_ms:.3f}ms")
        print(f"Cost:     $0.000 (no LLM calls)")
        print(f"Changed:  {result.refined_prompt != prompt}")

