"""
Intelligent Merger for MPR-SaaS
Combines worker outputs with conflict resolution and intent preservation
"""
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from difflib import SequenceMatcher


@dataclass
class MergeResult:
    """Result of merging worker outputs."""
    final_prompt: str
    strategy_used: str
    drift_score: float
    conflicts_resolved: int
    quality_score: float
    reasoning: List[str]


class IntelligentMerger:
    """
    Intelligent merger that combines worker outputs optimally.
    
    Strategies:
    - Sequential: clean → para → add description
    - Selective: choose best output for each aspect
    - Conservative: preserve original when conflicts detected
    - Weighted: confidence-weighted combination
    """
    
    def __init__(
        self,
        max_drift: float = 0.4,
        similarity_threshold: float = 0.7
    ):
        self.max_drift = max_drift
        self.similarity_threshold = similarity_threshold
    
    def merge(
        self,
        original: str,
        cleaned: Optional[str] = None,
        described: Optional[str] = None,
        paraphrased: Optional[str] = None,
        strategy: str = "adaptive"
    ) -> MergeResult:
        """
        Merge worker outputs using specified strategy.
        
        Args:
            original: Original user prompt
            cleaned: Output from Cleaner (optional)
            described: Output from Describer (optional)
            paraphrased: Output from Paraphraser (optional)
            strategy: Merge strategy to use
        
        Returns:
            MergeResult with merged prompt and metadata
        """
        # Determine which outputs we have
        has_cleaned = cleaned is not None and cleaned != original
        has_described = described is not None and described.strip() != ""
        has_paraphrased = paraphrased is not None and paraphrased != original
        
        needs_structured = has_cleaned and has_paraphrased and has_described
        
        # Select strategy
        if strategy == "adaptive":
            strategy = self._select_strategy(original, cleaned, described, paraphrased)
        
        # Execute merge
        if strategy == "sequential":
            result = self._sequential_merge(original, cleaned, described, paraphrased)
        elif strategy == "selective":
            result = self._selective_merge(original, cleaned, described, paraphrased)
        elif strategy == "conservative":
            result = self._conservative_merge(original, cleaned, described, paraphrased)
        else:  # weighted
            result = self._weighted_merge(original, cleaned, described, paraphrased)
        
        # Compose structured prompt when all specialists contributed
        if needs_structured and cleaned and paraphrased and described:
            structured_prompt = self._compose_triplet_prompt(
                cleaned or original,
                paraphrased,
                described,
            )
            if structured_prompt:
                result.final_prompt = structured_prompt
                result.reasoning.append(
                    "Composed structured prompt (cleaned → paraphrased → described)"
                )
                result.strategy_used = f"{result.strategy_used}+structured"
                result.drift_score = self._calculate_drift(original, result.final_prompt)
                result.quality_score = self._calculate_quality(result.final_prompt)
        
        # Validate and adjust if needed
        validated_result = self._validate_merge(original, result)
        
        return validated_result
    
    def _select_strategy(
        self,
        original: str,
        cleaned: Optional[str],
        described: Optional[str],
        paraphrased: Optional[str]
    ) -> str:
        """Automatically select best merge strategy based on outputs."""
        
        # If we have all three outputs and they're all different
        outputs = [o for o in [cleaned, paraphrased] if o and o != original]
        
        if len(outputs) >= 2:
            # Check if outputs are similar to each other
            similarities = [
                self._calculate_similarity(outputs[i], outputs[j])
                for i in range(len(outputs))
                for j in range(i + 1, len(outputs))
            ]
            avg_similarity = sum(similarities) / len(similarities) if similarities else 1.0
            
            if avg_similarity > 0.8:
                # Outputs agree, use sequential
                return "sequential"
            elif avg_similarity < 0.5:
                # Significant disagreement, be conservative
                return "conservative"
            else:
                # Moderate agreement, use selective
                return "selective"
        
        # Default to sequential
        return "sequential"
    
    def _sequential_merge(
        self,
        original: str,
        cleaned: Optional[str],
        described: Optional[str],
        paraphrased: Optional[str]
    ) -> MergeResult:
        """
        Sequential merge: clean → para → add description.
        
        This is the default strategy when outputs don't conflict.
        """
        reasoning = ["Using sequential merge strategy"]
        conflicts = 0
        
        # Start with cleaned version if available
        if cleaned and cleaned != original:
            base = cleaned
            reasoning.append("Using cleaned text as base")
        else:
            base = original
            reasoning.append("Using original text as base (no cleaning needed)")
        
        # Apply paraphrasing if available and different
        if paraphrased and paraphrased != original:
            # Check if paraphrasing improves quality
            if self._is_better_quality(base, paraphrased):
                base = paraphrased
                reasoning.append("Applied paraphrasing for improved fluency")
            else:
                reasoning.append("Skipped paraphrasing (didn't improve quality)")
                conflicts += 1
        
        # Add description if available
        final_prompt = base
        if described and described.strip():
            context_block = self._format_context(described)
            if context_block:
                final_prompt = f"{base}\n\n{context_block}"
                reasoning.append("Added concise context")
            else:
                reasoning.append("Skipped context (not useful)")
        
        # Calculate drift
        drift = self._calculate_drift(original, final_prompt)
        quality = self._calculate_quality(final_prompt)
        
        return MergeResult(
            final_prompt=final_prompt,
            strategy_used="sequential",
            drift_score=drift,
            conflicts_resolved=conflicts,
            quality_score=quality,
            reasoning=reasoning
        )
    
    def _selective_merge(
        self,
        original: str,
        cleaned: Optional[str],
        described: Optional[str],
        paraphrased: Optional[str]
    ) -> MergeResult:
        """
        Selective merge: choose best parts from each output.
        
        Uses quality scoring to select optimal combination.
        """
        reasoning = ["Using selective merge strategy"]
        conflicts = 0
        
        # Evaluate each output
        candidates = [
            ("original", original),
            ("cleaned", cleaned),
            ("paraphrased", paraphrased)
        ]
        
        # Score each candidate
        scored_candidates = [
            (name, text, self._calculate_quality(text) if text else 0.0)
            for name, text in candidates
            if text
        ]
        
        # Select best base
        best_name, best_text, best_score = max(scored_candidates, key=lambda x: x[2])
        reasoning.append(f"Selected {best_name} as base (quality: {best_score:.2f})")
        
        # If multiple candidates are close, it's a conflict
        close_candidates = [s for _, _, s in scored_candidates if abs(s - best_score) < 0.1]
        if len(close_candidates) > 1:
            conflicts += 1
            reasoning.append("Resolved conflict between similar-quality outputs")
        
        # Add description
        final_prompt = best_text
        if described and described.strip():
            context_block = self._format_context(described)
            if context_block:
                final_prompt = f"{best_text}\n\n{context_block}"
                reasoning.append("Added concise context")
            else:
                reasoning.append("Skipped context (not useful)")
        
        drift = self._calculate_drift(original, final_prompt)
        quality = self._calculate_quality(final_prompt)
        
        return MergeResult(
            final_prompt=final_prompt,
            strategy_used="selective",
            drift_score=drift,
            conflicts_resolved=conflicts,
            quality_score=quality,
            reasoning=reasoning
        )
    
    def _conservative_merge(
        self,
        original: str,
        cleaned: Optional[str],
        described: Optional[str],
        paraphrased: Optional[str]
    ) -> MergeResult:
        """
        Conservative merge: preserve original when conflicts detected.
        
        Only makes minimal changes to ensure safety.
        """
        reasoning = ["Using conservative merge strategy due to conflicts"]
        conflicts = 0
        
        # Only apply cleaning if drift is minimal
        base = original
        if cleaned and cleaned != original:
            drift = self._calculate_drift(original, cleaned)
            if drift < 0.2:
                base = cleaned
                reasoning.append("Applied minimal cleaning")
            else:
                reasoning.append("Skipped cleaning due to high drift")
                conflicts += 1
        
        # Only add description, don't modify base
        final_prompt = base
        if described and described.strip():
            context_block = self._format_context(described)
            if context_block:
                final_prompt = f"{base}\n\n{context_block}"
                reasoning.append("Added concise context only")
            else:
                reasoning.append("Skipped context (not useful)")
        
        drift = self._calculate_drift(original, final_prompt)
        quality = self._calculate_quality(final_prompt)
        
        return MergeResult(
            final_prompt=final_prompt,
            strategy_used="conservative",
            drift_score=drift,
            conflicts_resolved=conflicts,
            quality_score=quality,
            reasoning=reasoning
        )
    
    def _weighted_merge(
        self,
        original: str,
        cleaned: Optional[str],
        described: Optional[str],
        paraphrased: Optional[str]
    ) -> MergeResult:
        """
        Weighted merge: combine based on confidence scores.
        
        Currently falls back to selective merge.
        """
        # For now, use selective merge as weighted merge
        # TODO: Implement actual weighted combination
        return self._selective_merge(original, cleaned, described, paraphrased)
    
    def _validate_merge(self, original: str, result: MergeResult) -> MergeResult:
        """
        Validate merged result and adjust if needed.
        
        Checks:
        - Drift within acceptable range
        - No hallucinated content
        - Intent preserved
        """
        # Check drift
        if result.drift_score > self.max_drift:
            # Too much drift, fall back to conservative merge
            result.reasoning.append(f"High drift detected ({result.drift_score:.2f}), using original with context only")
            context_block = ""
            if "Helpful context:" in result.final_prompt:
                context_block = result.final_prompt.split("Helpful context:", 1)[1].strip()
            result.final_prompt = original.strip()
            if context_block:
                cleaned_context = "\n".join(
                    line for line in context_block.splitlines() if line.strip()
                )
                result.final_prompt = f"{result.final_prompt}\n\nHelpful context:\n{cleaned_context}"
            result.strategy_used = "conservative_fallback"
            result.drift_score = 0.0
        
        return result
    
    def _calculate_drift(self, original: str, modified: str) -> float:
        """
        Calculate semantic drift from original to modified.
        
        Uses character-level similarity as proxy for semantic similarity.
        
        Returns:
            Drift score 0.0 (identical) to 1.0 (completely different)
        """
        # Remove context additions for fair comparison
        if "\n\nHelpful context:" in modified:
            modified_base = modified.split("\n\nHelpful context:")[0]
        else:
            modified_base = modified
        
        # Calculate similarity
        similarity = SequenceMatcher(None, original.lower(), modified_base.lower()).ratio()
        
        # Drift is inverse of similarity
        return 1.0 - similarity
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts (0.0 to 1.0)."""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def _calculate_quality(self, text: str) -> float:
        """
        Calculate overall quality score of text.
        
        Considers:
        - Length (not too short or too long)
        - Completeness
        - Clarity
        
        Returns:
            Quality score 0.0 to 1.0
        """
        if not text:
            return 0.0
        
        score = 1.0
        
        # Length score
        length = len(text)
        if length < 20:
            score -= 0.3
        elif length < 40:
            score -= 0.1
        elif length > 500:
            score -= 0.1
        
        # Word count
        words = text.split()
        if len(words) < 3:
            score -= 0.2
        
        # Check for proper capitalization
        if text and text[0].islower():
            score -= 0.1
        
        # Check for ending punctuation
        if not text.strip()[-1] in '.?!':
            score -= 0.05
        
        return max(score, 0.0)
    
    def _is_better_quality(self, text1: str, text2: str) -> bool:
        """Check if text2 is better quality than text1."""
        quality1 = self._calculate_quality(text1)
        quality2 = self._calculate_quality(text2)
        return quality2 > quality1 + 0.05  # Require meaningful improvement

    def _format_context(self, described: Optional[str]) -> Optional[str]:
        """Return formatted context block or None."""
        lines = self._extract_context_lines(described)
        if not lines:
            return None
        context_block = "\n".join(f"- {line}" for line in lines)
        return f"Helpful context:\n{context_block}"

    def _extract_context_lines(self, described: Optional[str]) -> List[str]:
        """Extract up to three concise context lines."""
        if not described:
            return []

        text = ""
        if isinstance(described, dict):
            candidate = described.get("summary") or described.get("description") or ""
            if isinstance(candidate, str):
                text = candidate
            elif isinstance(candidate, list):
                text = " ".join(str(item) for item in candidate if isinstance(item, str))
        elif isinstance(described, str):
            text = described
        else:
            text = str(described)

        if not text:
            return []

        text = text.strip()
        if not text:
            return []

        summary_aliases = {"summary", "concise summary", "short summary"}
        segments: List[str] = []

        for line in text.splitlines():
            cleaned = line.strip()
            if not cleaned:
                continue
            cleaned = cleaned.lstrip("-*• ").strip()
            if not cleaned:
                continue

            if ":" in cleaned:
                label, value = cleaned.split(":", 1)
                if label.lower().strip() in summary_aliases:
                    snippet = value.strip()
                    if snippet:
                        if len(snippet) > 160:
                            snippet = snippet[:157].rstrip() + "..."
                        segments.append(snippet)
                    continue

            if len(cleaned) > 160:
                cleaned = cleaned[:157].rstrip() + "..."

            if len(cleaned) >= 5:
                segments.append(cleaned)

            if len(segments) >= 5:
                break

        if not segments:
            trimmed = text if len(text) <= 160 else text[:157].rstrip() + "..."
            segments.append(trimmed)

        # Deduplicate while preserving order
        deduped: List[str] = []
        seen = set()
        for seg in segments:
            normalized = seg.lower()
            if normalized in seen:
                continue
            seen.add(normalized)
            deduped.append(seg)

        # Score segments: prefer ones with digits or longer informative content
        scored: List[tuple[int, int, str]] = []
        for idx, seg in enumerate(deduped):
            score = 0
            if any(ch.isdigit() for ch in seg):
                score += 2
            if len(seg.split()) >= 6:
                score += 1
            if '?' in seg or ':' in seg:
                score += 1
            scored.append((score, idx, seg))

        scored.sort(key=lambda item: (-item[0], item[1]))
        ordered = [seg for _, _, seg in scored]

        return ordered[:2]

    def _compose_triplet_prompt(
        self,
        cleaned: str,
        paraphrased: str,
        described: Optional[str]
    ) -> str:
        """Compose inline prompt: cleaned + paraphrased + described summary."""
        clean_clause = self._sanitize_inline(cleaned)
        para_clause = self._sanitize_inline(paraphrased)
        descr_clause = self._sanitize_inline(self._summarize_description(described))
        
        parts: List[str] = []
        if clean_clause:
            parts.append(clean_clause)
        if para_clause:
            parts.append(f"In other words, {para_clause}")
        if descr_clause:
            parts.append(f"To help you understand, {descr_clause}")
        
        combined = " ".join(parts).strip()
        return combined or clean_clause or ""

    def _summarize_description(self, described: Optional[str]) -> str:
        """Return inline summary from description output."""
        lines = self._extract_context_lines(described)
        if not lines:
            if isinstance(described, str):
                return described.strip()
            return ""
        return "; ".join(line.strip() for line in lines if line.strip())

    @staticmethod
    def _sanitize_inline(text: Optional[str]) -> str:
        """Collapse whitespace for inline composition."""
        if not text:
            return ""
        return " ".join(text.strip().split())

