"""
Cost Calculation Module for MPR-SaaS Comparison

Converts token counts to USD costs using config/prices.yml
"""

import yaml
from pathlib import Path
from typing import Dict, Tuple

class CostCalculator:
    def __init__(self, prices_path: str = "/home/config/prices.yml"):
        with open(prices_path, 'r') as f:
            self.prices = yaml.safe_load(f)
    
    def get_model_cost(self, model_name: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for a model invocation"""
        if model_name not in self.prices['models']:
            raise ValueError(f"Unknown model: {model_name}")
        
        model_prices = self.prices['models'][model_name]
        input_cost = (input_tokens / 1_000_000) * model_prices['input']
        output_cost = (output_tokens / 1_000_000) * model_prices['output']
        return input_cost + output_cost
    
    def calculate_control_cost(self, prompt_tokens: int, response_tokens: int, 
                               target_model: str = "llama-3.1-70b") -> Dict:
        """Control baseline: no refinement"""
        cost = self.get_model_cost(target_model, prompt_tokens, response_tokens)
        return {
            "refinement_cost": 0.0,
            "target_llm_cost": cost,
            "total_cost": cost,
            "method": "control"
        }
    
    def calculate_template_cost(self, prompt_tokens: int, response_tokens: int,
                                target_model: str = "llama-3.1-70b") -> Dict:
        """Template baseline: minimal overhead"""
        overhead = self.prices['baselines']['template']['overhead_tokens']
        augmented_tokens = prompt_tokens + overhead
        cost = self.get_model_cost(target_model, augmented_tokens, response_tokens)
        return {
            "refinement_cost": 0.0,  # Negligible
            "target_llm_cost": cost,
            "total_cost": cost,
            "method": "template",
            "overhead_tokens": overhead
        }
    
    def calculate_cot_cost(self, prompt_tokens: int, response_tokens: int,
                           target_model: str = "llama-3.1-70b") -> Dict:
        """Chain-of-thought baseline: minimal overhead"""
        overhead = self.prices['baselines']['cot']['overhead_tokens']
        augmented_tokens = prompt_tokens + overhead
        cost = self.get_model_cost(target_model, augmented_tokens, response_tokens)
        return {
            "refinement_cost": 0.0,  # Negligible
            "target_llm_cost": cost,
            "total_cost": cost,
            "method": "cot",
            "overhead_tokens": overhead
        }
    
    def calculate_gpt4_refine_cost(self, prompt_tokens: int, response_tokens: int,
                                   refinement_in: int = 100, refinement_out: int = 100,
                                   target_model: str = "llama-3.1-70b") -> Dict:
        """GPT-4 refinement baseline"""
        refine_cost = self.get_model_cost("gpt-4o", refinement_in, refinement_out)
        target_cost = self.get_model_cost(target_model, prompt_tokens, response_tokens)
        return {
            "refinement_cost": refine_cost,
            "target_llm_cost": target_cost,
            "total_cost": refine_cost + target_cost,
            "method": "gpt4_refine",
            "refinement_tokens": refinement_in + refinement_out
        }
    
    def calculate_claude_refine_cost(self, prompt_tokens: int, response_tokens: int,
                                     refinement_in: int = 100, refinement_out: int = 100,
                                     target_model: str = "llama-3.1-70b") -> Dict:
        """Claude refinement baseline"""
        refine_cost = self.get_model_cost("claude-3-5-sonnet", refinement_in, refinement_out)
        target_cost = self.get_model_cost(target_model, prompt_tokens, response_tokens)
        return {
            "refinement_cost": refine_cost,
            "target_llm_cost": target_cost,
            "total_cost": refine_cost + target_cost,
            "method": "claude_refine",
            "refinement_tokens": refinement_in + refinement_out
        }
    
    def calculate_mpr_saas_cost(self, prompt_tokens: int, response_tokens: int,
                                cleaner_tokens: Tuple[int, int] = (50, 50),
                                describer_tokens: Tuple[int, int] = (50, 150),
                                paraphraser_tokens: Tuple[int, int] = (50, 60),
                                target_model: str = "llama-3.1-70b") -> Dict:
        """MPR-SaaS: 3 parallel workers + target LLM"""
        # Cleaner cost
        cleaner_cost = self.get_model_cost("llama-3.2-3b", cleaner_tokens[0], cleaner_tokens[1])
        
        # Describer cost
        describer_cost = self.get_model_cost("llama-3.2-3b", describer_tokens[0], describer_tokens[1])
        
        # Paraphraser cost
        paraphraser_cost = self.get_model_cost("llama-3.2-3b", paraphraser_tokens[0], paraphraser_tokens[1])
        
        # Total refinement cost (parallel, but all 3 run)
        refinement_cost = cleaner_cost + describer_cost + paraphraser_cost
        
        # Target LLM cost (prompt is now augmented with description)
        augmented_prompt_tokens = prompt_tokens + describer_tokens[1]  # Added description
        target_cost = self.get_model_cost(target_model, augmented_prompt_tokens, response_tokens)
        
        return {
            "refinement_cost": refinement_cost,
            "cleaner_cost": cleaner_cost,
            "describer_cost": describer_cost,
            "paraphraser_cost": paraphraser_cost,
            "target_llm_cost": target_cost,
            "total_cost": refinement_cost + target_cost,
            "method": "mpr_saas",
            "refinement_tokens": sum([sum(t) for t in [cleaner_tokens, describer_tokens, paraphraser_tokens]])
        }
    
    def compare_costs(self, prompt_tokens: int = 100, response_tokens: int = 200,
                      target_model: str = "llama-3.1-70b") -> Dict:
        """Compare costs across all methods"""
        control = self.calculate_control_cost(prompt_tokens, response_tokens, target_model)
        template = self.calculate_template_cost(prompt_tokens, response_tokens, target_model)
        cot = self.calculate_cot_cost(prompt_tokens, response_tokens, target_model)
        gpt4 = self.calculate_gpt4_refine_cost(prompt_tokens, response_tokens, target_model=target_model)
        claude = self.calculate_claude_refine_cost(prompt_tokens, response_tokens, target_model=target_model)
        mpr = self.calculate_mpr_saas_cost(prompt_tokens, response_tokens, target_model=target_model)
        
        results = {
            "control": control,
            "template": template,
            "cot": cot,
            "gpt4_refine": gpt4,
            "claude_refine": claude,
            "mpr_saas": mpr
        }
        
        # Calculate relative costs
        baseline_cost = control['total_cost']
        for method, data in results.items():
            data['relative_cost'] = data['total_cost'] / baseline_cost
            data['cost_increase_pct'] = (data['relative_cost'] - 1.0) * 100
        
        return results


if __name__ == "__main__":
    calc = CostCalculator()
    
    print("="*80)
    print("MPR-SaaS Cost Comparison (Typical Query)")
    print("="*80)
    print(f"\nAssumptions:")
    print(f"  - Prompt: 100 tokens")
    print(f"  - Response: 200 tokens")
    print(f"  - Target LLM: Llama 3.1 70B (local)")
    print()
    
    results = calc.compare_costs(prompt_tokens=100, response_tokens=200)
    
    print(f"\n{'Method':<20} {'Refine Cost':<15} {'Target Cost':<15} {'Total Cost':<15} {'vs Control':<12}")
    print("="*80)
    
    for method, data in results.items():
        print(f"{method:<20} ${data['refinement_cost']:<14.6f} ${data['target_llm_cost']:<14.6f} "
              f"${data['total_cost']:<14.6f} {data['cost_increase_pct']:>+6.1f}%")
    
    print("\n" + "="*80)
    print("KEY FINDINGS:")
    print("="*80)
    
    control_cost = results['control']['total_cost']
    mpr_cost = results['mpr_saas']['total_cost']
    gpt4_cost = results['gpt4_refine']['total_cost']
    claude_cost = results['claude_refine']['total_cost']
    
    print(f"\n✅ MPR-SaaS adds {results['mpr_saas']['cost_increase_pct']:.1f}% cost vs Control")
    print(f"✅ MPR-SaaS is {gpt4_cost/mpr_cost:.1f}x cheaper than GPT-4 refinement")
    print(f"✅ MPR-SaaS is {claude_cost/mpr_cost:.1f}x cheaper than Claude refinement")
    print()

