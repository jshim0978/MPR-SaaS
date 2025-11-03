#!/bin/bash
# Quick Comparison Test - Run What We Have Now
# Tests 8 methods on sample prompts

set -e

echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║          QUICK COMPARISON TEST - 8 METHODS READY                          ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""

cd /home/comparison

# Test prompts with common issues
TEST_PROMPTS=(
    "what is the captial of frane?"
    "tell me about quantom physics"
    "how does photosythesis work"
    "explain climate change pls"
    "whats the difference btw virus and bacteria"
)

echo "📋 Test Prompts:"
for i in "${!TEST_PROMPTS[@]}"; do
    echo "  $((i+1)). ${TEST_PROMPTS[$i]}"
done
echo ""

# Create simple test runner
python3 << 'PYEOF'
import sys
sys.path.append('/home/comparison')
sys.path.append('/home/comparison/frameworks')
sys.path.append('/home/comparison/baselines')

from baselines.control import ControlBaseline
from baselines.template import TemplateBaseline
from baselines.cot import CoTBaseline

test_prompts = [
    "what is the captial of frane?",
    "tell me about quantom physics",
    "how does photosythesis work"
]

print("="*80)
print("QUICK COMPARISON: SIMPLE BASELINES (No API Keys Needed)")
print("="*80)

methods = [
    ("Control", ControlBaseline()),
    ("Template", TemplateBaseline()),
    ("CoT", CoTBaseline())
]

for prompt in test_prompts:
    print(f"\n📝 Original: {prompt}")
    print("-"*80)
    
    for name, method in methods:
        result = method.refine(prompt)
        print(f"\n{name:12} → {result['refined_prompt'][:60]}...")
        print(f"             Latency: {result['refinement_latency_ms']:.2f}ms | "
              f"Tokens: {result['prompt_tokens']} | "
              f"Added: +{result['refinement_tokens_added']}")
    
    print("")

print("\n" + "="*80)
print("✅ SIMPLE BASELINES TEST COMPLETE")
print("="*80)
print("")
print("💡 To test SOTA methods (OPRO, PromptBreeder):")
print("   Set OPENAI_API_KEY environment variable")
print("   Then run: python3 frameworks/opro/opro_1iter.py")
print("")
print("💡 To test MPR-SaaS:")
print("   Ensure workers are running (jw2, jw3, kcloud, jw1)")
print("   Then run: python3 baselines/mpr_saas.py")
print("")

PYEOF

echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                         NEXT STEPS                                        ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "1️⃣  Test with API keys (optional):"
echo "    export OPENAI_API_KEY='sk-...'"
echo "    python3 frameworks/opro/opro_1iter.py"
echo ""
echo "2️⃣  Test MPR-SaaS when workers ready:"
echo "    python3 baselines/mpr_saas.py"
echo ""
echo "3️⃣  Run full comparison (when all ready):"
echo "    bash run_all.sh"
echo ""


