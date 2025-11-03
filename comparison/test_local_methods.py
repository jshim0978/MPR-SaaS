#!/usr/bin/env python3
"""
Test Runner for All Methods - LOCAL LLAMA VERSION

Tests all methods using Llama-3.2-3B and Llama-3.1-8B base models.
No OpenAI API keys required!
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'frameworks'))

from baselines.control import ControlBaseline
from baselines.template import TemplateBaseline
from baselines.cot import CoTBaseline
from frameworks.ado.format_normalizer import ADO_FormatOnly

# Local Llama versions
MPR_AVAILABLE = os.environ.get("ORCHESTRATOR_URL") is not None


def print_section(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}")


def test_simple_baselines():
    print_section("TESTING SIMPLE BASELINES (No API Keys, No vLLM)")
    
    methods = [
        ControlBaseline(),
        TemplateBaseline(),
        CoTBaseline(),
        ADO_FormatOnly()
    ]
    
    test_prompt = "what is the captial of frane?"
    
    for method in methods:
        try:
            result = method.refine(test_prompt)
            status = "✅" if not result.error else f"❌ {result.error}"
            print(f"{status} {method.name:25s} → {result.refined_prompt[:50]}...")
            print(f"   Latency: {result.latency_ms:.3f}ms | Tokens: {result.tokens_used}")
        except Exception as e:
            print(f"❌ {method.name:25s} → ERROR: {e}")
    
    return len(methods)


def test_local_sota_methods():
    print_section("TESTING SOTA METHODS (Local Llama via vLLM)")
    print("Requires: vLLM server running on localhost:8001")
    print("Start with: vllm serve meta-llama/Llama-3.2-3B-Instruct --port 8001")
    print("="*80)
    
    import asyncio
    from frameworks.opro.opro_local import OPRO_Local
    from frameworks.promptagent.strategic_local import PromptAgent_Local
    from frameworks.protegi.gradient_local import ProTeGi_Local
    from frameworks.promptbreeder.evolutionary_local import PromptBreeder_Local
    from frameworks.selfcheckgpt.detector_local import SelfCheckGPT_Local
    from frameworks.cove.verifier_local import CoVe_Local
    
    test_prompt = "what is the captial of frane?"
    tested = 0
    
    async def test_method(method_class, model_size, prompt, method_name):
        try:
            method = method_class(model_size=model_size)
            result = await method.refine(prompt)
            status = "✅" if not result.error else f"❌ {result.error}"
            print(f"{status} {method.name:35s} → {result.refined_prompt[:40]}...")
            print(f"   Latency: {result.latency_ms:.1f}ms | Tokens: {result.tokens_used} | Cost: ${method.calculate_cost(result.tokens_used):.6f}")
            return True
        except Exception as e:
            print(f"❌ {method_name}_{model_size.upper():3s} → ERROR: {e}")
            return False
    
    async def run_all_tests():
        total_tested = 0
        
        # Test each method with both 3B and 8B models
        methods_to_test = [
            (OPRO_Local, "OPRO_Local"),
            (PromptAgent_Local, "PromptAgent_Local"),
            (ProTeGi_Local, "ProTeGi_Local"),
        ]
        
        for method_class, method_name in methods_to_test:
            for model_size in ["3b", "8b"]:
                result = await test_method(method_class, model_size, test_prompt, method_name)
                if result:
                    total_tested += 1
        
        # PromptBreeder and CoVe are expensive, test only 3B
        print(f"\n⚡ Testing expensive methods (3B only):")
        if await test_method(PromptBreeder_Local, "3b", test_prompt, "PromptBreeder_Local"):
            total_tested += 1
        
        if await test_method(SelfCheckGPT_Local, "3b", test_prompt, "SelfCheckGPT_Local"):
            total_tested += 1
        
        if await test_method(CoVe_Local, "3b", test_prompt, "CoVe_Local"):
            total_tested += 1
        
        return total_tested
    
    try:
        tested = asyncio.run(run_all_tests())
    except Exception as e:
        print(f"\n❌ vLLM server not running or error: {e}")
        print("   Start vLLM with: vllm serve meta-llama/Llama-3.2-3B-Instruct --port 8001")
        tested = 0
    
    return tested


def test_mpr_saas():
    if not MPR_AVAILABLE:
        print_section("SKIPPING MPR-SaaS (Workers Not Running)")
        print("Deploy workers on jw2, jw3, kcloud and jw1 orchestrator to test")
        print("Set ORCHESTRATOR_URL=http://129.254.202.251:8000 to enable")
        return 0
    
    print_section("TESTING MPR-SaaS (Our System)")
    
    try:
        from baselines.mpr_saas import MPRSaasBaseline
        import asyncio
        
        method = MPRSaasBaseline()
        test_prompt = "what is the captial of frane?"
        
        result = asyncio.run(method.refine(test_prompt))
        status = "✅" if not result.error else f"❌ {result.error}"
        print(f"{status} {method.name:25s} → {result.refined_prompt[:50]}...")
        print(f"   Latency: {result.latency_ms:.1f}ms | Tokens: {result.tokens_used}")
        return 1
    except Exception as e:
        print(f"❌ MPR-SaaS → ERROR: {e}")
        return 0


def main():
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║     COMPREHENSIVE TEST: LOCAL LLAMA COMPARISON (NO OPENAI NEEDED!)       ║
╚═══════════════════════════════════════════════════════════════════════════╝
""")
    
    tested_simple = test_simple_baselines()
    tested_sota = test_local_sota_methods()
    tested_mpr = test_mpr_saas()
    
    total_tested = tested_simple + tested_sota + tested_mpr
    
    print_section("SUMMARY")
    print(f"\n✅ Simple Baselines:   {tested_simple}/4 tested")
    print(f"{'✅' if tested_sota > 0 else '⏭️ '} SOTA Methods (Local): {tested_sota}/9 tested (3B+8B variants)")
    print(f"{'✅' if tested_mpr > 0 else '⏭️ '} MPR-SaaS:           {tested_mpr}/1 tested")
    print(f"\n{'='*80}")
    print(f"TOTAL TESTED: {total_tested}/14 methods")
    print(f"{'='*80}")
    
    print("\n💡 To enable vLLM tests:")
    print("   vllm serve meta-llama/Llama-3.2-3B-Instruct --port 8001")
    print("   (or use Llama-3.1-8B-Instruct for 8B model)")
    
    print("\n💡 To enable MPR-SaaS:")
    print("   export ORCHESTRATOR_URL='http://129.254.202.251:8000'")
    
    print("\n🚀 Ready for full evaluation with LOCAL MODELS ONLY!")
    print("   All methods use your Llama-3.2-3B and Llama-3.1-8B models")
    print("   No OpenAI costs! Pure local comparison!")


if __name__ == "__main__":
    main()

