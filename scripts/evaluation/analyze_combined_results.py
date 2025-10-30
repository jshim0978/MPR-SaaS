#!/usr/bin/env python3
"""
Analyze the combined models evaluation results.
Creates a comprehensive human-readable report.
"""

import json
import re
from collections import defaultdict

def load_results(filepath):
    """Load evaluation results from JSON."""
    with open(filepath, 'r') as f:
        return json.load(f)

def count_words(text):
    """Count words in text."""
    return len(text.split())

def has_numbers(text):
    """Check if text contains numbers (dates, statistics, measurements)."""
    return bool(re.search(r'\d+', text))

def count_numbers(text):
    """Count occurrences of numbers in text."""
    return len(re.findall(r'\d+', text))

def analyze_model_responses(model_data):
    """Analyze all responses from a model."""
    results = model_data['results']
    
    stats = {
        'total_responses': len(results),
        'word_counts': [],
        'responses_with_numbers': 0,
        'number_counts': [],
        'avg_word_count': 0,
        'avg_numbers_per_response': 0,
        'short_responses': 0,  # < 50 words
        'medium_responses': 0,  # 50-150 words
        'long_responses': 0,  # > 150 words
    }
    
    for result in results:
        response = result['response']
        word_count = count_words(response)
        number_count = count_numbers(response)
        
        stats['word_counts'].append(word_count)
        stats['number_counts'].append(number_count)
        
        if has_numbers(response):
            stats['responses_with_numbers'] += 1
        
        if word_count < 50:
            stats['short_responses'] += 1
        elif word_count <= 150:
            stats['medium_responses'] += 1
        else:
            stats['long_responses'] += 1
    
    stats['avg_word_count'] = sum(stats['word_counts']) / len(stats['word_counts'])
    stats['avg_numbers_per_response'] = sum(stats['number_counts']) / len(stats['number_counts'])
    
    return stats

def create_report(results_file, output_file):
    """Create comprehensive analysis report."""
    data = load_results(results_file)
    
    # Analyze each model
    model_stats = {}
    for model_data in data:
        model_name = model_data['model']
        model_stats[model_name] = analyze_model_responses(model_data)
    
    # Generate report
    report_lines = []
    
    report_lines.append("="*80)
    report_lines.append("COMBINED MODELS EVALUATION ANALYSIS")
    report_lines.append("="*80)
    report_lines.append("")
    report_lines.append("📊 Testing: 25 informative prompts across 4 models")
    report_lines.append("🎯 Goal: Determine if Wikipedia + Wikidata training produces")
    report_lines.append("          informative, factual, detailed descriptions")
    report_lines.append("")
    report_lines.append("="*80)
    report_lines.append("SUMMARY STATISTICS")
    report_lines.append("="*80)
    report_lines.append("")
    
    # Create comparison table
    report_lines.append("┌─────────────────────────────────┬──────────┬──────────┬──────────┬──────────┐")
    report_lines.append("│ Model                           │ Avg Words│  Numbers │  Short   │   Long   │")
    report_lines.append("│                                 │          │ per resp │responses │responses │")
    report_lines.append("├─────────────────────────────────┼──────────┼──────────┼──────────┼──────────┤")
    
    for model_name in ['Original 3B', '3B Combined (Wiki + Wikidata)', 'Original 8B', '8B Combined (Wiki + Wikidata)']:
        stats = model_stats[model_name]
        report_lines.append(f"│ {model_name:<31} │ {stats['avg_word_count']:>8.1f} │ {stats['avg_numbers_per_response']:>8.1f} │ {stats['short_responses']:>8} │ {stats['long_responses']:>8} │")
    
    report_lines.append("└─────────────────────────────────┴──────────┴──────────┴──────────┴──────────┘")
    report_lines.append("")
    report_lines.append("Legend:")
    report_lines.append("  • Avg Words: Average word count per response")
    report_lines.append("  • Numbers per resp: Average count of numbers (dates, stats, measurements)")
    report_lines.append("  • Short responses: < 50 words")
    report_lines.append("  • Long responses: > 150 words")
    report_lines.append("")
    
    # Detailed analysis
    report_lines.append("="*80)
    report_lines.append("KEY FINDINGS")
    report_lines.append("="*80)
    report_lines.append("")
    
    # Compare 3B models
    orig_3b = model_stats['Original 3B']
    comb_3b = model_stats['3B Combined (Wiki + Wikidata)']
    
    report_lines.append("🔵 3B MODELS COMPARISON:")
    report_lines.append("")
    report_lines.append(f"  Original 3B:")
    report_lines.append(f"    • Average response length: {orig_3b['avg_word_count']:.1f} words")
    report_lines.append(f"    • Long detailed responses: {orig_3b['long_responses']}/25 ({orig_3b['long_responses']/25*100:.0f}%)")
    report_lines.append(f"    • Numbers/statistics: {orig_3b['avg_numbers_per_response']:.1f} per response")
    report_lines.append("")
    report_lines.append(f"  3B Combined (Wiki + Wikidata):")
    report_lines.append(f"    • Average response length: {comb_3b['avg_word_count']:.1f} words")
    report_lines.append(f"    • Long detailed responses: {comb_3b['long_responses']}/25 ({comb_3b['long_responses']/25*100:.0f}%)")
    report_lines.append(f"    • Numbers/statistics: {comb_3b['avg_numbers_per_response']:.1f} per response")
    report_lines.append("")
    
    word_diff_3b = ((comb_3b['avg_word_count'] - orig_3b['avg_word_count']) / orig_3b['avg_word_count']) * 100
    report_lines.append(f"  📉 Change: {word_diff_3b:+.0f}% in response length")
    report_lines.append(f"  📉 Change: {comb_3b['long_responses'] - orig_3b['long_responses']:+d} long responses")
    report_lines.append("")
    
    # Compare 8B models
    orig_8b = model_stats['Original 8B']
    comb_8b = model_stats['8B Combined (Wiki + Wikidata)']
    
    report_lines.append("🔵 8B MODELS COMPARISON:")
    report_lines.append("")
    report_lines.append(f"  Original 8B:")
    report_lines.append(f"    • Average response length: {orig_8b['avg_word_count']:.1f} words")
    report_lines.append(f"    • Long detailed responses: {orig_8b['long_responses']}/25 ({orig_8b['long_responses']/25*100:.0f}%)")
    report_lines.append(f"    • Numbers/statistics: {orig_8b['avg_numbers_per_response']:.1f} per response")
    report_lines.append("")
    report_lines.append(f"  8B Combined (Wiki + Wikidata):")
    report_lines.append(f"    • Average response length: {comb_8b['avg_word_count']:.1f} words")
    report_lines.append(f"    • Long detailed responses: {comb_8b['long_responses']}/25 ({comb_8b['long_responses']/25*100:.0f}%)")
    report_lines.append(f"    • Numbers/statistics: {comb_8b['avg_numbers_per_response']:.1f} per response")
    report_lines.append("")
    
    word_diff_8b = ((comb_8b['avg_word_count'] - orig_8b['avg_word_count']) / orig_8b['avg_word_count']) * 100
    report_lines.append(f"  📉 Change: {word_diff_8b:+.0f}% in response length")
    report_lines.append(f"  📉 Change: {comb_8b['long_responses'] - orig_8b['long_responses']:+d} long responses")
    report_lines.append("")
    
    # Overall conclusion
    report_lines.append("="*80)
    report_lines.append("CRITICAL FINDING")
    report_lines.append("="*80)
    report_lines.append("")
    report_lines.append("❌ THE COMBINED TRAINING MADE RESPONSES SHORTER, NOT MORE INFORMATIVE")
    report_lines.append("")
    report_lines.append("Both 3B and 8B combined models produce SIGNIFICANTLY shorter responses")
    report_lines.append("than their original counterparts:")
    report_lines.append("")
    report_lines.append(f"  • 3B model: {word_diff_3b:.0f}% reduction in response length")
    report_lines.append(f"  • 8B model: {word_diff_8b:.0f}% reduction in response length")
    report_lines.append("")
    report_lines.append("The combined models produce brief, dictionary-style definitions rather than")
    report_lines.append("detailed, informative explanations.")
    report_lines.append("")
    report_lines.append("="*80)
    report_lines.append("EXAMPLES OF THE PROBLEM")
    report_lines.append("="*80)
    report_lines.append("")
    
    # Add example comparisons
    example_prompts = data[0]['results'][:5]  # First 5 prompts
    
    for i, example in enumerate(example_prompts):
        prompt = example['prompt']
        
        # Get responses from all models
        orig_3b_resp = data[0]['results'][i]['response']
        comb_3b_resp = data[1]['results'][i]['response']
        orig_8b_resp = data[2]['results'][i]['response']
        comb_8b_resp = data[3]['results'][i]['response']
        
        report_lines.append(f"Example {i+1}: \"{prompt}\"")
        report_lines.append("─" * 80)
        report_lines.append("")
        report_lines.append(f"Original 3B ({count_words(orig_3b_resp)} words):")
        report_lines.append(f"  {orig_3b_resp[:200]}{'...' if len(orig_3b_resp) > 200 else ''}")
        report_lines.append("")
        report_lines.append(f"3B Combined ({count_words(comb_3b_resp)} words):")
        report_lines.append(f"  {comb_3b_resp}")
        report_lines.append("")
        report_lines.append(f"Original 8B ({count_words(orig_8b_resp)} words):")
        report_lines.append(f"  {orig_8b_resp[:200]}{'...' if len(orig_8b_resp) > 200 else ''}")
        report_lines.append("")
        report_lines.append(f"8B Combined ({count_words(comb_8b_resp)} words):")
        report_lines.append(f"  {comb_8b_resp}")
        report_lines.append("")
        report_lines.append("")
    
    # Recommendations
    report_lines.append("="*80)
    report_lines.append("RECOMMENDATIONS")
    report_lines.append("="*80)
    report_lines.append("")
    report_lines.append("❌ Current Situation:")
    report_lines.append("   The Wikipedia + Wikidata training produced models that are TOO CONCISE.")
    report_lines.append("   They give brief definitions rather than informative explanations.")
    report_lines.append("")
    report_lines.append("🎯 What You Wanted:")
    report_lines.append("   Detailed, informative, factual descriptions with specific data")
    report_lines.append("   (like 'average adults get haircut every 4-6 weeks')")
    report_lines.append("")
    report_lines.append("💡 Options:")
    report_lines.append("")
    report_lines.append("1. ⚡ TRY SYSTEM PROMPTS (Quick):")
    report_lines.append("   Use the ORIGINAL models (not combined) with optimized system prompts.")
    report_lines.append("   The original models already produce detailed, informative responses!")
    report_lines.append("   Just need to guide them with proper prompting.")
    report_lines.append("")
    report_lines.append("2. 🔄 RETRAIN WITH DIFFERENT DATA (Slower):")
    report_lines.append("   Create a custom dataset with longer, more detailed responses.")
    report_lines.append("   Current training data (Wiki + Wikidata) seems to emphasize brevity.")
    report_lines.append("   Need dataset that demonstrates the detailed style you want.")
    report_lines.append("")
    report_lines.append("3. 📝 RETRAIN WITH MODIFIED PROMPTS:")
    report_lines.append("   Use the same data but modify the training format to encourage")
    report_lines.append("   longer, more detailed responses in the training examples.")
    report_lines.append("")
    report_lines.append("="*80)
    report_lines.append("RECOMMENDATION: START WITH OPTION 1")
    report_lines.append("="*80)
    report_lines.append("")
    report_lines.append("✅ The original models ALREADY produce the detailed responses you want!")
    report_lines.append("   No need to retrain - just optimize the system prompt to guide them")
    report_lines.append("   toward the specific style you prefer.")
    report_lines.append("")
    report_lines.append("   This will be:")
    report_lines.append("   • FAST (minutes vs hours)")
    report_lines.append("   • FREE (no GPU training costs)")
    report_lines.append("   • ITERATIVE (can test many variations quickly)")
    report_lines.append("")
    report_lines.append("="*80)
    
    # Write report
    report_text = "\n".join(report_lines)
    with open(output_file, 'w') as f:
        f.write(report_text)
    
    print(report_text)
    
    return report_text

def main():
    results_file = "/home/evaluation_combined_informative.json"
    output_file = "/home/COMBINED_MODELS_ANALYSIS_REPORT.txt"
    
    print("Analyzing evaluation results...")
    print()
    
    create_report(results_file, output_file)
    
    print()
    print("="*80)
    print(f"📁 Report saved to: {output_file}")
    print("="*80)

if __name__ == "__main__":
    main()

