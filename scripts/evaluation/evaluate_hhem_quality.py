#!/usr/bin/env python3
"""
Evaluate Wikipedia-focused models using HHEM-style quality scoring.
Focus: Information quality and helpfulness, not just length.
"""

import json
import re
from typing import Dict, List, Tuple

def load_results(filepath):
    """Load evaluation results from JSON."""
    with open(filepath, 'r') as f:
        return json.load(f)

def extract_key_facts(reference):
    """Extract key facts from reference answer."""
    # Extract numbers, years, proper nouns, and key terms
    numbers = set(re.findall(r'\b\d+\b', reference))
    
    # Common key terms in our test set
    key_terms = set()
    words = reference.lower().split()
    for word in words:
        if len(word) > 3 and word not in ['the', 'and', 'with', 'from', 'that', 'this', 'have', 'been', 'were']:
            key_terms.add(word)
    
    return {
        'numbers': numbers,
        'key_terms': key_terms
    }

def score_response_quality(response: str, reference: str, prompt: str) -> Dict:
    """
    Score response quality based on HHEM-style criteria.
    Returns a quality score focusing on informativeness and accuracy.
    """
    response_lower = response.lower()
    reference_lower = reference.lower()
    
    score = {
        'factual_accuracy': 0,      # Does it contain correct facts? (0-3)
        'completeness': 0,           # Does it answer the question fully? (0-3)
        'informativeness': 0,        # Does it provide useful context? (0-3)
        'relevance': 0,              # Is it on-topic? (0-1)
        'total_score': 0,            # Total score (0-10)
        'quality_category': ''       # High/Medium/Low
    }
    
    # Extract key facts
    key_facts = extract_key_facts(reference)
    response_numbers = set(re.findall(r'\b\d+\b', response))
    
    # 1. FACTUAL ACCURACY (0-3 points)
    # Check if response contains key numbers/facts
    numbers_match = len(key_facts['numbers'] & response_numbers)
    terms_match = sum(1 for term in key_facts['key_terms'] if term in response_lower)
    
    if numbers_match >= len(key_facts['numbers']) * 0.8 and terms_match >= len(key_facts['key_terms']) * 0.5:
        score['factual_accuracy'] = 3  # Excellent
    elif numbers_match >= len(key_facts['numbers']) * 0.5 and terms_match >= len(key_facts['key_terms']) * 0.3:
        score['factual_accuracy'] = 2  # Good
    elif numbers_match > 0 or terms_match > 0:
        score['factual_accuracy'] = 1  # Fair
    else:
        score['factual_accuracy'] = 0  # Poor
    
    # 2. COMPLETENESS (0-3 points)
    # Very short answers (< 5 words) are likely incomplete unless the question is very simple
    word_count = len(response.split())
    
    if word_count >= 20:
        score['completeness'] = 3  # Likely provides complete answer with context
    elif word_count >= 10:
        score['completeness'] = 2  # Provides answer with some context
    elif word_count >= 3:
        score['completeness'] = 1  # Minimal answer
    else:
        score['completeness'] = 0  # Too brief
    
    # Adjust for simple questions where brief is ok
    simple_question_keywords = ['capital', 'chemical formula', 'symbol']
    if any(kw in prompt.lower() for kw in simple_question_keywords):
        if word_count >= 3:
            score['completeness'] = max(score['completeness'], 2)
    
    # 3. INFORMATIVENESS (0-3 points)
    # Does it provide context, explanations, or additional useful info?
    info_indicators = [
        'because', 'however', 'also', 'additionally', 'known as',
        'consists of', 'composed of', 'officially', 'approximately',
        'located', 'founded', 'established', 'developed', 'invented',
        'named after', 'refers to', 'means that'
    ]
    
    info_count = sum(1 for indicator in info_indicators if indicator in response_lower)
    has_explanation = any(word in response_lower for word in ['is', 'are', 'was', 'were', 'means', 'refers'])
    
    if info_count >= 3 and word_count >= 30:
        score['informativeness'] = 3  # Rich in context
    elif info_count >= 2 or (has_explanation and word_count >= 15):
        score['informativeness'] = 2  # Some context
    elif has_explanation or word_count >= 10:
        score['informativeness'] = 1  # Minimal context
    else:
        score['informativeness'] = 0  # No context
    
    # 4. RELEVANCE (0-1 point)
    # Is the response on-topic?
    prompt_keywords = set(re.findall(r'\b\w{4,}\b', prompt.lower()))
    response_keywords = set(re.findall(r'\b\w{4,}\b', response_lower))
    
    overlap = len(prompt_keywords & response_keywords)
    if overlap >= len(prompt_keywords) * 0.3 or any(term in response_lower for term in reference_lower.split()[:3]):
        score['relevance'] = 1
    else:
        score['relevance'] = 0
    
    # Calculate total
    score['total_score'] = (
        score['factual_accuracy'] + 
        score['completeness'] + 
        score['informativeness'] + 
        score['relevance']
    )
    
    # Categorize quality
    if score['total_score'] >= 8:
        score['quality_category'] = 'High'
    elif score['total_score'] >= 5:
        score['quality_category'] = 'Medium'
    else:
        score['quality_category'] = 'Low'
    
    return score

def evaluate_model_quality(model_data):
    """Evaluate quality scores for all responses from a model."""
    results = model_data['results']
    
    stats = {
        'total_questions': len(results),
        'avg_factual_accuracy': 0,
        'avg_completeness': 0,
        'avg_informativeness': 0,
        'avg_relevance': 0,
        'avg_total_score': 0,
        'high_quality': 0,
        'medium_quality': 0,
        'low_quality': 0,
        'all_scores': []
    }
    
    for result in results:
        quality = score_response_quality(
            result['response'],
            result['reference'],
            result['prompt']
        )
        
        stats['all_scores'].append(quality)
        stats['avg_factual_accuracy'] += quality['factual_accuracy']
        stats['avg_completeness'] += quality['completeness']
        stats['avg_informativeness'] += quality['informativeness']
        stats['avg_relevance'] += quality['relevance']
        stats['avg_total_score'] += quality['total_score']
        
        if quality['quality_category'] == 'High':
            stats['high_quality'] += 1
        elif quality['quality_category'] == 'Medium':
            stats['medium_quality'] += 1
        else:
            stats['low_quality'] += 1
    
    # Calculate averages
    n = stats['total_questions']
    stats['avg_factual_accuracy'] /= n
    stats['avg_completeness'] /= n
    stats['avg_informativeness'] /= n
    stats['avg_relevance'] /= n
    stats['avg_total_score'] /= n
    
    return stats

def create_quality_report(results_file, output_file):
    """Create HHEM-style quality analysis report."""
    data = load_results(results_file)
    
    # Analyze each model
    model_stats = {}
    for model_data in data:
        model_name = model_data['model']
        model_stats[model_name] = evaluate_model_quality(model_data)
    
    # Generate report
    report_lines = []
    
    report_lines.append("="*80)
    report_lines.append("HHEM-STYLE QUALITY EVALUATION")
    report_lines.append("="*80)
    report_lines.append("")
    report_lines.append("📊 Measuring: Information quality and helpfulness (not just length)")
    report_lines.append("🎯 Scoring Criteria:")
    report_lines.append("   • Factual Accuracy (0-3): Contains correct facts and numbers")
    report_lines.append("   • Completeness (0-3): Fully answers the question")
    report_lines.append("   • Informativeness (0-3): Provides useful context and explanations")
    report_lines.append("   • Relevance (0-1): On-topic and addresses the question")
    report_lines.append("   • Total Score (0-10): Overall quality score")
    report_lines.append("")
    report_lines.append("="*80)
    report_lines.append("QUALITY SCORES SUMMARY")
    report_lines.append("="*80)
    report_lines.append("")
    
    # Create comparison table
    report_lines.append("┌──────────────────────────────────┬───────┬──────────┬──────────┬──────────┐")
    report_lines.append("│ Model                            │ Total │ Accuracy │ Complete │ Informtv │")
    report_lines.append("│                                  │ Score │  (0-3)   │  (0-3)   │  (0-3)   │")
    report_lines.append("├──────────────────────────────────┼───────┼──────────┼──────────┼──────────┤")
    
    for model_name in sorted(model_stats.keys()):
        stats = model_stats[model_name]
        report_lines.append(
            f"│ {model_name:<32} │ {stats['avg_total_score']:>5.1f} │ {stats['avg_factual_accuracy']:>8.2f} │ "
            f"{stats['avg_completeness']:>8.2f} │ {stats['avg_informativeness']:>8.2f} │"
        )
    
    report_lines.append("└──────────────────────────────────┴───────┴──────────┴──────────┴──────────┘")
    report_lines.append("")
    report_lines.append("┌──────────────────────────────────┬──────────┬──────────┬──────────┐")
    report_lines.append("│ Model                            │   High   │  Medium  │   Low    │")
    report_lines.append("│                                  │ Quality  │ Quality  │ Quality  │")
    report_lines.append("├──────────────────────────────────┼──────────┼──────────┼──────────┤")
    
    for model_name in sorted(model_stats.keys()):
        stats = model_stats[model_name]
        report_lines.append(
            f"│ {model_name:<32} │ {stats['high_quality']:>8} │ {stats['medium_quality']:>8} │ {stats['low_quality']:>8} │"
        )
    
    report_lines.append("└──────────────────────────────────┴──────────┴──────────┴──────────┘")
    report_lines.append("")
    
    # Rankings
    report_lines.append("="*80)
    report_lines.append("QUALITY RANKINGS")
    report_lines.append("="*80)
    report_lines.append("")
    
    by_total = sorted(model_stats.items(), key=lambda x: x[1]['avg_total_score'], reverse=True)
    
    report_lines.append("🏆 OVERALL QUALITY (by total score):")
    report_lines.append("")
    for i, (model_name, stats) in enumerate(by_total, 1):
        report_lines.append(
            f"  {i}. {model_name}: {stats['avg_total_score']:.1f}/10 "
            f"({stats['high_quality']} high, {stats['medium_quality']} medium, {stats['low_quality']} low)"
        )
    report_lines.append("")
    
    # By specific criteria
    by_accuracy = sorted(model_stats.items(), key=lambda x: x[1]['avg_factual_accuracy'], reverse=True)
    by_info = sorted(model_stats.items(), key=lambda x: x[1]['avg_informativeness'], reverse=True)
    
    report_lines.append("📊 BY FACTUAL ACCURACY:")
    for i, (model_name, stats) in enumerate(by_accuracy[:3], 1):
        report_lines.append(f"  {i}. {model_name}: {stats['avg_factual_accuracy']:.2f}/3")
    report_lines.append("")
    
    report_lines.append("📚 BY INFORMATIVENESS:")
    for i, (model_name, stats) in enumerate(by_info[:3], 1):
        report_lines.append(f"  {i}. {model_name}: {stats['avg_informativeness']:.2f}/3")
    report_lines.append("")
    
    # Detailed comparison
    report_lines.append("="*80)
    report_lines.append("KEY INSIGHTS")
    report_lines.append("="*80)
    report_lines.append("")
    
    best = by_total[0]
    worst = by_total[-1]
    
    report_lines.append(f"🏆 BEST: {best[0]}")
    report_lines.append(f"   • Total Quality Score: {best[1]['avg_total_score']:.1f}/10")
    report_lines.append(f"   • High-quality responses: {best[1]['high_quality']}/20")
    
    strengths = []
    if best[1]['avg_factual_accuracy'] >= 2.5:
        strengths.append("Excellent factual accuracy")
    if best[1]['avg_informativeness'] >= 2.5:
        strengths.append("Highly informative")
    if best[1]['avg_completeness'] >= 2.5:
        strengths.append("Complete answers")
    strengths_text = ", ".join(strengths) if strengths else "Well-balanced"
    report_lines.append(f"   • Strengths: {strengths_text}")
    report_lines.append("")
    report_lines.append("")
    
    report_lines.append(f"⚠️  WORST: {worst[0]}")
    report_lines.append(f"   • Total Quality Score: {worst[1]['avg_total_score']:.1f}/10")
    report_lines.append(f"   • High-quality responses: {worst[1]['high_quality']}/20")
    
    issues = []
    if worst[1]['avg_informativeness'] < 1.0:
        issues.append("Lacks context")
    if worst[1]['avg_completeness'] < 1.0:
        issues.append("Incomplete answers")
    if worst[1]['avg_factual_accuracy'] < 2.0:
        issues.append("Missing key facts")
    issues_text = ", ".join(issues) if issues else "Low information density"
    report_lines.append(f"   • Issues: {issues_text}")
    report_lines.append("")
    report_lines.append("")
    
    # Sample detailed scores
    report_lines.append("="*80)
    report_lines.append("SAMPLE QUALITY SCORES (Question #3: When did World War II end?)")
    report_lines.append("="*80)
    report_lines.append("")
    
    sample_idx = 2  # WWII question
    for model_data in data:
        model_name = model_data['model']
        stats = model_stats[model_name]
        quality = stats['all_scores'][sample_idx]
        response = model_data['results'][sample_idx]['response']
        word_count = len(response.split())
        
        report_lines.append(f"{model_name}:")
        report_lines.append(f"  Response: \"{response[:80]}{'...' if len(response) > 80 else ''}\" ({word_count}w)")
        report_lines.append(f"  Scores: Accuracy={quality['factual_accuracy']}/3, "
                          f"Complete={quality['completeness']}/3, "
                          f"Info={quality['informativeness']}/3 → "
                          f"Total={quality['total_score']}/10 ({quality['quality_category']})")
        report_lines.append("")
    
    # Recommendations
    report_lines.append("="*80)
    report_lines.append("RECOMMENDATIONS")
    report_lines.append("="*80)
    report_lines.append("")
    
    best_model = by_total[0][0]
    best_score = by_total[0][1]['avg_total_score']
    
    report_lines.append(f"✅ RECOMMENDED MODEL: {best_model}")
    report_lines.append(f"   Quality Score: {best_score:.1f}/10")
    report_lines.append(f"   This model provides the best balance of accuracy, completeness,")
    report_lines.append(f"   and informativeness for helping answer questions correctly.")
    report_lines.append("")
    
    # Write report
    report_text = "\n".join(report_lines)
    with open(output_file, 'w') as f:
        f.write(report_text)
    
    print(report_text)
    
    return report_text

def main():
    results_file = "/home/evaluation_wiki_models_only.json"
    output_file = "/home/HHEM_QUALITY_REPORT.txt"
    
    print("Analyzing response quality using HHEM-style scoring...")
    print()
    
    create_quality_report(results_file, output_file)
    
    print()
    print("="*80)
    print(f"📁 Report saved to: {output_file}")
    print("="*80)

if __name__ == "__main__":
    main()

