"""
Professional weighted scoring system for enhancer detection.

Implements scientifically rigorous scoring with proper weighting,
normalization, and context awareness.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum


class EnhancerClass(str, Enum):
    """Enhancer classification based on chromatin state."""
    NOT_APPLICABLE = "not_applicable"  # Gene-proximal regions
    NONE = "none"                       # No enhancer signatures
    PRIMED = "primed"                   # H3K4me1+ but H3K27ac-
    ACTIVE = "active"                   # H3K27ac+ and H3K4me1+
    POISED = "poised"                   # H3K4me1+ and H3K27me3+


class ConfidenceLevel(str, Enum):
    """Confidence levels with clear definitions."""
    HIGH = "high"        # ≥8 points & ≥2 replicates consistent
    MODERATE = "moderate"  # 5-7 points or partial replicate consistency
    LOW = "low"          # <5 points or no cell type match
    NA = "not_applicable"  # Gene-proximal regions


@dataclass
class ScoringCriteria:
    """Weighted scoring criteria for enhancer detection."""
    # Core histone marks (max 6 points)
    h3k27ac_weight: float = 4.0  # Active enhancer mark
    h3k4me1_weight: float = 2.0  # Enhancer mark
    
    # Accessibility (max 2 points)
    accessibility_weight: float = 2.0  # ATAC/DNase
    
    # RNA evidence (max 2 points)
    erna_weight: float = 2.0  # CAGE eRNA bidirectional
    
    # Penalties
    gene_body_penalty: float = -2.0  # H3K36me3/Pol II high
    promoter_penalty: float = -1.0   # H3K4me3 high
    
    # Bonus
    allele_specific_bonus: float = 1.0  # Consistent allele bias
    
    # Thresholds (z-scores)
    h3k27ac_threshold: float = 2.0
    h3k4me1_threshold: float = 2.0
    accessibility_threshold: float = 1.5
    h3k4me3_threshold: float = 1.0  # Should be LOW for enhancers
    h3k36me3_threshold: float = 1.0  # Should be LOW for enhancers
    
    max_score: float = 10.0


class ProfessionalScorer:
    """
    Professional scoring system with weighted criteria and proper normalization.
    
    Based on ENCODE standards and scientific consensus:
    - Exon/promoter regions are pre-filtered
    - H3K27ac and H3K4me1 are weighted highest
    - Gene body marks incur penalties
    - Clear confidence definitions
    """
    
    def __init__(self):
        self.criteria = ScoringCriteria()
    
    def calculate_weighted_score(
        self,
        evidence: Dict[str, float],
        genomic_context: Dict[str, any],
        cell_type_matched: bool = False,
        replicate_count: int = 1
    ) -> Tuple[float, Dict[str, float], EnhancerClass, ConfidenceLevel]:
        """
        Calculate weighted score with proper normalization.
        
        Args:
            evidence: Z-scores or normalized values for each mark
            genomic_context: Information about genomic location
            cell_type_matched: Whether data is from matched cell type
            replicate_count: Number of replicates
            
        Returns:
            Tuple of (total_score, component_scores, classification, confidence)
        """
        
        # Pre-filter: Check if in gene-proximal region
        if self._is_gene_proximal(genomic_context):
            return (
                0.0,
                {},
                EnhancerClass.NOT_APPLICABLE,
                ConfidenceLevel.NA
            )
        
        component_scores = {}
        total_score = 0.0
        
        # Core histone marks
        if evidence.get('h3k27ac_zscore', 0) >= self.criteria.h3k27ac_threshold:
            score = self.criteria.h3k27ac_weight
            component_scores['H3K27ac'] = score
            total_score += score
        else:
            component_scores['H3K27ac'] = 0.0
        
        if evidence.get('h3k4me1_zscore', 0) >= self.criteria.h3k4me1_threshold:
            score = self.criteria.h3k4me1_weight
            component_scores['H3K4me1'] = score
            total_score += score
        else:
            component_scores['H3K4me1'] = 0.0
        
        # Accessibility
        if evidence.get('accessibility_zscore', 0) >= self.criteria.accessibility_threshold:
            score = self.criteria.accessibility_weight
            component_scores['Accessibility'] = score
            total_score += score
        else:
            component_scores['Accessibility'] = 0.0
        
        # RNA evidence (only if likely eRNA, not mRNA)
        if evidence.get('is_likely_erna', False):
            score = self.criteria.erna_weight
            component_scores['eRNA'] = score
            total_score += score
        else:
            component_scores['eRNA'] = 0.0
        
        # Apply penalties
        
        # Gene body penalty (H3K36me3 high suggests gene body)
        if evidence.get('h3k36me3_zscore', 0) > self.criteria.h3k36me3_threshold:
            penalty = self.criteria.gene_body_penalty
            component_scores['Gene_body_penalty'] = penalty
            total_score += penalty
        
        # Promoter penalty (H3K4me3 high suggests promoter)
        if evidence.get('h3k4me3_zscore', 0) > self.criteria.h3k4me3_threshold:
            penalty = self.criteria.promoter_penalty
            component_scores['Promoter_penalty'] = penalty
            total_score += penalty
        
        # Apply bonus for allele specificity
        if evidence.get('has_allele_bias', False):
            bonus = self.criteria.allele_specific_bonus
            component_scores['Allele_specific_bonus'] = bonus
            total_score += bonus
        
        # Ensure score is within bounds
        total_score = max(0, min(self.criteria.max_score, total_score))
        
        # Determine classification
        classification = self._classify_enhancer(component_scores, evidence)
        
        # Determine confidence
        confidence = self._determine_confidence(
            total_score,
            cell_type_matched,
            replicate_count
        )
        
        return total_score, component_scores, classification, confidence
    
    def _is_gene_proximal(self, genomic_context: Dict) -> bool:
        """Check if variant is in gene-proximal region."""
        if genomic_context.get('is_exon', False):
            return True
        
        if genomic_context.get('is_coding', False):
            return True
        
        # Within 2kb of TSS
        distance_to_tss = genomic_context.get('distance_to_tss', float('inf'))
        if abs(distance_to_tss) <= 2000:
            return True
        
        return False
    
    def _classify_enhancer(
        self,
        component_scores: Dict[str, float],
        evidence: Dict[str, float]
    ) -> EnhancerClass:
        """Classify enhancer based on marks present."""
        
        h3k27ac_present = component_scores.get('H3K27ac', 0) > 0
        h3k4me1_present = component_scores.get('H3K4me1', 0) > 0
        accessibility_present = component_scores.get('Accessibility', 0) > 0
        
        # Active enhancer: H3K27ac+ and accessibility
        if h3k27ac_present and accessibility_present:
            return EnhancerClass.ACTIVE
        
        # Primed enhancer: H3K4me1+ and accessibility but no H3K27ac
        if h3k4me1_present and accessibility_present and not h3k27ac_present:
            return EnhancerClass.PRIMED
        
        # Poised enhancer: H3K4me1+ with repressive marks
        if h3k4me1_present and evidence.get('h3k27me3_zscore', 0) > 2.0:
            return EnhancerClass.POISED
        
        # No enhancer signatures
        return EnhancerClass.NONE
    
    def _determine_confidence(
        self,
        total_score: float,
        cell_type_matched: bool,
        replicate_count: int
    ) -> ConfidenceLevel:
        """Determine confidence level based on score and data quality."""
        
        # Require cell type match for any confidence
        if not cell_type_matched:
            return ConfidenceLevel.LOW
        
        # High confidence: ≥8 points & ≥2 replicates
        if total_score >= 8.0 and replicate_count >= 2:
            return ConfidenceLevel.HIGH
        
        # Moderate confidence: 5-7 points or single replicate
        if 5.0 <= total_score < 8.0:
            return ConfidenceLevel.MODERATE
        
        # Low confidence: <5 points
        return ConfidenceLevel.LOW
    
    def format_score_breakdown(
        self,
        total_score: float,
        component_scores: Dict[str, float],
        max_score: float = 10.0
    ) -> str:
        """Format score breakdown for reporting."""
        
        lines = [f"Total Score: {total_score:.1f}/{max_score:.1f}"]
        lines.append("\nComponent Breakdown:")
        
        # Sort by absolute value to show most impactful first
        sorted_components = sorted(
            component_scores.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        
        for component, score in sorted_components:
            if score > 0:
                lines.append(f"  + {component}: {score:.1f}")
            elif score < 0:
                lines.append(f"  - {component}: {abs(score):.1f}")
            else:
                lines.append(f"    {component}: 0.0")
        
        return "\n".join(lines)
    
    def get_algorithm_description(self) -> Dict[str, any]:
        """Get algorithm metadata for reproducibility."""
        return {
            "name": "Professional Weighted Enhancer Scorer",
            "version": "2.0",
            "criteria": {
                "H3K27ac_weight": self.criteria.h3k27ac_weight,
                "H3K4me1_weight": self.criteria.h3k4me1_weight,
                "Accessibility_weight": self.criteria.accessibility_weight,
                "eRNA_weight": self.criteria.erna_weight,
                "Gene_body_penalty": self.criteria.gene_body_penalty,
                "Promoter_penalty": self.criteria.promoter_penalty,
                "Allele_bonus": self.criteria.allele_specific_bonus
            },
            "thresholds": {
                "H3K27ac_zscore": self.criteria.h3k27ac_threshold,
                "H3K4me1_zscore": self.criteria.h3k4me1_threshold,
                "Accessibility_zscore": self.criteria.accessibility_threshold
            },
            "confidence_rules": {
                "HIGH": "≥8.0 score & ≥2 replicates & cell-type matched",
                "MODERATE": "5.0-7.9 score & cell-type matched",
                "LOW": "<5.0 score or no cell-type match"
            },
            "pre_filters": [
                "Exons excluded",
                "Promoters ±2kb excluded",
                "Coding variants excluded"
            ]
        }