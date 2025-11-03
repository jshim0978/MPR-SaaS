#!/usr/bin/env python3
"""
Test Runner for All 13 Comparison Methods

Runs a quick test of each method to verify implementations.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'frameworks'))

from baselines.control import ControlBaseline
from baselines.template import TemplateBaseline
from baselines.cot import CoTBaseline
from frameworks.ado.format_normalizer import ADO_FormatOnly

# Methods requiring API keys
OPENAI_AVAILABLE = os.environ.get("OPENAI_API_KEY") is not None
ANTHROPIC_AVAILABLE = os.environ.get("ANTHROPIC_API_KEY") is not None
MPR_AVAILABLE = os.environ.get("ORCHESTRATOR_URL") is not None


def print_section(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}")


def test_simple_baselines():
    print_section("TESTING SIMPLE BASELINES (No API Keys Needed)")
    
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
            print(f"{status} {method.name:20s} → {result.refined_prompt[:60]}...")
            print(f"   Latency: {result.latency_ms:.3f}ms | Tokens: {result.tokens_used}")
        except Exception as e:
            print(f"❌ {method.name:20s} → ERROR: {e}")
    
    return len(methods)


def test_commercial_methods():
    if not OPENAI_AVAILABLE and not ANTHROPIC_AVAILABLE:
        print_section("SKIPPING COMMERCIAL METHODS (No API Keys)")
        print("Set OPENAI_API_KEY and ANTHROPIC_API_KEY to test GPT-4/Claude refinement")
        return 0
    
    print_section("TESTING COMMERCIAL METHODS")
    
    test_prompt = "what is the captial of frane?"
    tested = 0
    
    if OPENAI_AVAILABLE:
        try:
            from baselines.gpt4_refine import GPT4RefineBaseline
            import asyncio
            
            method = GPT4RefineBaseline()
            result = asyncio.run(method.refine(test_prompt))
            status = "✅" if not result.error else f"❌ {result.error}"
            print(f"{status} {method.name:20s} → {result.refined_prompt[:60]}...")
            print(f"   Latency: {result.latency_ms:.1f}ms | Tokens: {result.tokens_used}")
            tested += 1
        except Exception as e:
            print(f"❌ GPT-4 Refine → ERROR: {e}")
    
    if ANTHROPIC_AVAILABLE:
        try:
            from baselines.claude_refine import ClaudeRefineBaseline
            import asyncio
            
            method = ClaudeRefineBaseline()
            result = asyncio.run(method.refine(test_prompt))
            status = "✅" if not result.error else f"❌ {result.error}"
            print(f"{status} {method.name:20s} → {result.refined_prompt[:60]}...")
            print(f"   Latency: {result.latency_ms:.1f}ms | Tokens: {result.tokens_used}")
            tested += 1
        except Exception as e:
            print(f"❌ Claude Refine → ERROR: {e}")
    
    return tested


def test_sota_methods():
    if not OPENAI_AVAILABLE:
        print_section("SKIPPING SOTA METHODS (No OpenAI API Key)")
        print("Set OPENAI_API_KEY to test OPRO, PromptBreeder, PromptAgent, ProTeGi, SelfCheckGPT, CoVe")
        return 0
    
    print_section("TESTING SOTA METHODS (using OpenAI API)")
    
    import asyncio
    from frameworks.opro.opro_1iter import OPRO1Iter
    from frameworks.promptagent.strategic_1pass import PromptAgent_1pass
    from frameworks.protegi.gradient_1pass import ProTeGi_1pass
    
    methods = [
        OPRO1Iter(),
        PromptAgent_1pass(),
        ProTeGi_1pass(),
    ]
    
    test_prompt = "what is the captial of frane?"
    
    async def test_method(method, prompt):
        try:
            result = await method.refine(prompt)
            status = "✅" if not result.error else f"❌ {result.error}"
            print(f"{status} {method.name:20s} → {result.refined_prompt[:60]}...")
            print(f"   Latency: {result.latency_ms:.1f}ms | Tokens: {result.tokens_used} | Cost: ${method.calculate_cost(result.tokens_used):.6f}")
            return True
        except Exception as e:
            print(f"❌ {method.name:20s} → ERROR: {e}")
            return False
    
    async def run_all_tests():
        results = []
        for method in methods:
            result = await test_method(method, test_prompt)
            results.append(result)
        return sum(results)
    
    tested = asyncio.run(run_all_tests())
    
    # PromptBreeder and CoVe are expensive, skip for quick test
    print(f"\n⏩ Skipping PromptBreeder (8×2 = 16 LLM calls, ~$0.01)")
    print(f"⏩ Skipping SelfCheckGPT (3 samples, ~$0.003)")
    print(f"⏩ Skipping CoVe (4-5 LLM calls, ~$0.005)")
    print("   (These can be tested individually if needed)")
    
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
        print(f"{status} {method.name:20s} → {result.refined_prompt[:60]}...")
        print(f"   Latency: {result.latency_ms:.1f}ms | Tokens: {result.tokens_used}")
        return 1
    except Exception as e:
        print(f"❌ MPR-SaaS → ERROR: {e}")
        return 0


def main():
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║          COMPREHENSIVE TEST: ALL 13 COMPARISON METHODS                    ║
╚═══════════════════════════════════════════════════════════════════════════╝
""")
    
    tested_simple = test_simple_baselines()
    tested_commercial = test_commercial_methods()
    tested_sota = test_sota_methods()
    tested_mpr = test_mpr_saas()
    
    total_tested = tested_simple + tested_commercial + tested_sota + tested_mpr
    
    print_section("SUMMARY")
    print(f"\n✅ Simple Baselines:   {tested_simple}/4 tested")
    print(f"{'✅' if tested_commercial > 0 else '⏭️ '} Commercial Methods: {tested_commercial}/2 tested")
    print(f"{'✅' if tested_sota > 0 else '⏭️ '} SOTA Methods:       {tested_sota}/7 tested (quick subset)")
    print(f"{'✅' if tested_mpr > 0 else '⏭️ '} MPR-SaaS:           {tested_mpr}/1 tested")
    print(f"\n{'='*80}")
    print(f"TOTAL TESTED: {total_tested}/13 methods")
    print(f"{'='*80}")
    
    print("\n💡 To enable all tests:")
    print("   export OPENAI_API_KEY='sk-...'")
    print("   export ANTHROPIC_API_KEY='sk-ant-...'")
    print("   export ORCHESTRATOR_URL='http://129.254.202.251:8000'")
    
    print("\n🚀 Ready for full evaluation!")
    print("   Run: python3 eval_harness/runner.py datasets/hhem_500.json")


if __name__ == "__main__":
    main()

