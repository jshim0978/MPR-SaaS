#!/usr/bin/env python3
"""
Analyze Wikipedia-focused models evaluation results.
"""

import json
import re

def load_results(filepath):
    """Load evaluation results from JSON."""
    with open(filepath, 'r') as f:
        return json.load(f)

def count_words(text):
    """Count words in text."""
    return len(text.split())

def analyze_model_results(model_data):
    """Analyze all results for a model."""
    results = model_data['results']
    
    stats = {
        'total_questions': len(results),
        'word_counts': [],
        'avg_word_count': 0,
        'very_short': 0,  # < 15 words
        'short': 0,       # 15-30 words
        'medium': 0,      # 30-75 words
        'long': 0,        # 75-150 words
        'very_long': 0    # > 150 words
    }
    
    for result in results:
        response = result['response']
        word_count = count_words(response)
        stats['word_counts'].append(word_count)
        
        if word_count < 15:
            stats['very_short'] += 1
        elif word_count < 30:
            stats['short'] += 1
        elif word_count < 75:
            stats['medium'] += 1
        elif word_count < 150:
            stats['long'] += 1
        else:
            stats['very_long'] += 1
    
    stats['avg_word_count'] = sum(stats['word_counts']) / len(stats['word_counts'])
    stats['min_words'] = min(stats['word_counts'])
    stats['max_words'] = max(stats['word_counts'])
    
    return stats

def create_report(results_file, output_file):
    """Create comprehensive analysis report."""
    data = load_results(results_file)
    
    # Analyze each model
    model_stats = {}
    for model_data in data:
        model_name = model_data['model']
        model_stats[model_name] = analyze_model_results(model_data)
    
    # Generate report
    report_lines = []
    
    report_lines.append("="*80)
    report_lines.append("WIKIPEDIA-FOCUSED MODELS ANALYSIS")
    report_lines.append("="*80)
    report_lines.append("")
    report_lines.append("📊 Testing: 6 models (3B and 8B) × 3 training approaches")
    report_lines.append("🎯 Goal: Find detailed, informative, non-conversational responses")
    report_lines.append("")
    report_lines.append("="*80)
    report_lines.append("SUMMARY STATISTICS")
    report_lines.append("="*80)
    report_lines.append("")
    
    # Create comparison table
    report_lines.append("┌──────────────────────────────────┬──────────┬───────────┬───────────┬──────────┐")
    report_lines.append("│ Model                            │ Avg Words│ Very Short│  Medium   │   Long   │")
    report_lines.append("│                                  │          │   (<15w)  │ (30-75w)  │  (>75w)  │")
    report_lines.append("├──────────────────────────────────┼──────────┼───────────┼───────────┼──────────┤")
    
    for model_name in sorted(model_stats.keys()):
        stats = model_stats[model_name]
        long_count = stats['long'] + stats['very_long']
        report_lines.append(f"│ {model_name:<32} │ {stats['avg_word_count']:>8.1f} │ {stats['very_short']:>9} │ {stats['medium']:>9} │ {long_count:>8} │")
    
    report_lines.append("└──────────────────────────────────┴──────────┴───────────┴───────────┴──────────┘")
    report_lines.append("")
    
    # Detailed comparison
    report_lines.append("="*80)
    report_lines.append("DETAILED BREAKDOWN")
    report_lines.append("="*80)
    report_lines.append("")
    
    for model_name in sorted(model_stats.keys()):
        stats = model_stats[model_name]
        report_lines.append(f"{model_name}:")
        report_lines.append(f"  • Average: {stats['avg_word_count']:.1f} words")
        report_lines.append(f"  • Range: {stats['min_words']}-{stats['max_words']} words")
        report_lines.append(f"  • Very Short (<15w): {stats['very_short']}/20")
        report_lines.append(f"  • Short (15-30w): {stats['short']}/20")
        report_lines.append(f"  • Medium (30-75w): {stats['medium']}/20")
        report_lines.append(f"  • Long (75-150w): {stats['long']}/20")
        report_lines.append(f"  • Very Long (>150w): {stats['very_long']}/20")
        report_lines.append("")
    
    # Key findings
    report_lines.append("="*80)
    report_lines.append("KEY FINDINGS")
    report_lines.append("="*80)
    report_lines.append("")
    
    # Find best performing models
    by_avg_words = sorted(model_stats.items(), key=lambda x: x[1]['avg_word_count'], reverse=True)
    
    report_lines.append("📊 RANKING BY RESPONSE LENGTH (most detailed first):")
    report_lines.append("")
    for i, (model_name, stats) in enumerate(by_avg_words, 1):
        long_count = stats['long'] + stats['very_long']
        report_lines.append(f"  {i}. {model_name}: {stats['avg_word_count']:.1f} words avg, {long_count}/20 detailed")
    report_lines.append("")
    
    # Compare training approaches
    report_lines.append("🔍 BY TRAINING APPROACH:")
    report_lines.append("")
    
    wiki_only_models = {k: v for k, v in model_stats.items() if 'Wikipedia-only' in k}
    wikidata_only_models = {k: v for k, v in model_stats.items() if 'Wikidata-only' in k}
    combined_models = {k: v for k, v in model_stats.items() if 'Wiki+Wikidata' in k}
    
    wiki_avg = sum(s['avg_word_count'] for s in wiki_only_models.values()) / len(wiki_only_models)
    wikidata_avg = sum(s['avg_word_count'] for s in wikidata_only_models.values()) / len(wikidata_only_models)
    combined_avg = sum(s['avg_word_count'] for s in combined_models.values()) / len(combined_models)
    
    report_lines.append(f"  Wikipedia-only:      {wiki_avg:.1f} words average")
    report_lines.append(f"  Wikidata-only:       {wikidata_avg:.1f} words average")
    report_lines.append(f"  Wiki+Wikidata:       {combined_avg:.1f} words average")
    report_lines.append("")
    
    # Sample responses
    report_lines.append("="*80)
    report_lines.append("SAMPLE RESPONSES")
    report_lines.append("="*80)
    report_lines.append("")
    
    # Show 3 example questions
    example_indices = [0, 2, 5]  # Capital of France, WWII, Chemical formula
    
    for idx in example_indices:
        if idx < len(data[0]['results']):
            sample = data[0]['results'][idx]
            report_lines.append(f"Q: {sample['prompt']}")
            report_lines.append(f"Expected: {sample['reference']}")
            report_lines.append("─" * 80)
            
            for model_data in data:
                model_name = model_data['model']
                response = model_data['results'][idx]['response']
                word_count = count_words(response)
                
                report_lines.append(f"\n{model_name} ({word_count} words):")
                if len(response) > 200:
                    report_lines.append(f"  {response[:200]}...")
                else:
                    report_lines.append(f"  {response}")
            
            report_lines.append("")
            report_lines.append("")
    
    # Recommendations
    report_lines.append("="*80)
    report_lines.append("RECOMMENDATIONS")
    report_lines.append("="*80)
    report_lines.append("")
    
    best_model = by_avg_words[0][0]
    best_stats = by_avg_words[0][1]
    
    report_lines.append(f"🏆 BEST PERFORMING MODEL: {best_model}")
    report_lines.append(f"   • Average: {best_stats['avg_word_count']:.1f} words")
    report_lines.append(f"   • Detailed responses: {best_stats['long'] + best_stats['very_long']}/20")
    report_lines.append("")
    
    if wiki_avg > max(wikidata_avg, combined_avg):
        report_lines.append("✅ RECOMMENDATION: Use Wikipedia-only training")
        report_lines.append("   Wikipedia-only models provide the most detailed responses.")
    elif combined_avg > max(wiki_avg, wikidata_avg):
        report_lines.append("✅ RECOMMENDATION: Use Wiki+Wikidata combined training")
        report_lines.append("   Combined training provides best balance of detail and breadth.")
    else:
        report_lines.append("⚠️  Wikidata-only models are too concise for your needs.")
        report_lines.append("   Consider Wikipedia-only or combined approach.")
    
    report_lines.append("")
    report_lines.append("="*80)
    
    # Write report
    report_text = "\n".join(report_lines)
    with open(output_file, 'w') as f:
        f.write(report_text)
    
    print(report_text)
    
    return report_text

def main():
    results_file = "/home/evaluation_wiki_models_only.json"
    output_file = "/home/WIKI_MODELS_ANALYSIS_REPORT.txt"
    
    print("\nAnalyzing Wikipedia-focused models evaluation...")
    print()
    
    create_report(results_file, output_file)
    
    print()
    print("="*80)
    print(f"📁 Report saved to: {output_file}")
    print("="*80)

if __name__ == "__main__":
    main()

