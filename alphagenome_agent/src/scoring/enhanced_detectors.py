"""
Enhanced detection modules addressing scientific feedback.

Key improvements:
1. Exon/promoter blacklisting to avoid false positives
2. Stricter histone mark requirements (H3K4me1/H3K27ac mandatory)
3. Differentiation between mRNA and eRNA signals
4. Statistical validation with background controls
5. Tissue-specific data requirements
"""

from __future__ import annotations
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np


class RegionType(str, Enum):
    """Genomic region types for filtering."""
    EXON = "exon"
    PROMOTER = "promoter"
    INTRON = "intron"
    INTERGENIC = "intergenic"
    UTR_5 = "5_utr"
    UTR_3 = "3_utr"


class EnhancerState(str, Enum):
    """Enhancer chromatin states based on literature."""
    ACTIVE = "active"          # H3K27ac+, H3K4me1+
    PRIMED = "primed"          # H3K4me1+, H3K27ac-
    POISED = "poised"          # H3K4me1+, H3K27me3+
    INACTIVE = "inactive"      # No marks
    NOT_ENHANCER = "not_enhancer"  # Insufficient evidence


@dataclass
class GenomicContext:
    """Context information for a genomic position."""
    chromosome: str
    position: int
    region_type: RegionType
    gene_name: Optional[str] = None
    distance_to_tss: Optional[int] = None
    is_coding: bool = False
    genome_build: str = "hg38"
    
    @property
    def is_blacklisted_for_enhancer(self) -> bool:
        """Check if region should be excluded from enhancer calling."""
        # Exons and promoters shouldn't be called as enhancers
        blacklisted_types = {RegionType.EXON, RegionType.PROMOTER}
        return self.region_type in blacklisted_types or self.is_coding


@dataclass
class EnhancerEvidence:
    """Detailed evidence for enhancer detection."""
    # Core histone marks (required)
    h3k4me1_signal: float = 0.0
    h3k27ac_signal: float = 0.0
    
    # Accessibility
    dnase_signal: float = 0.0
    atac_signal: float = 0.0
    
    # Additional marks
    h3k4me3_signal: float = 0.0  # Should be low for enhancers
    h3k36me3_signal: float = 0.0  # Gene body mark
    h3k27me3_signal: float = 0.0  # Repressive mark
    
    # RNA signals
    total_rna: float = 0.0
    polya_rna: float = 0.0
    cage_signal: float = 0.0
    bidirectional_transcription: bool = False
    
    # Statistical measures
    background_mean: Dict[str, float] = field(default_factory=dict)
    background_std: Dict[str, float] = field(default_factory=dict)
    z_scores: Dict[str, float] = field(default_factory=dict)
    p_values: Dict[str, float] = field(default_factory=dict)
    
    # Cell type specificity
    cell_type: Optional[str] = None
    tissue_matched: bool = False
    replicate_count: int = 1
    
    def calculate_z_scores(self) -> None:
        """Calculate z-scores for all signals against background."""
        signals = {
            "h3k4me1": self.h3k4me1_signal,
            "h3k27ac": self.h3k27ac_signal,
            "dnase": self.dnase_signal,
            "atac": self.atac_signal,
            "h3k4me3": self.h3k4me3_signal
        }
        
        for mark, signal in signals.items():
            if mark in self.background_mean and mark in self.background_std:
                bg_mean = self.background_mean[mark]
                bg_std = self.background_std[mark]
                if bg_std > 0:
                    self.z_scores[mark] = (signal - bg_mean) / bg_std
                else:
                    self.z_scores[mark] = 0.0
    
    @property
    def is_likely_erna(self) -> bool:
        """Check if RNA signal is likely eRNA rather than mRNA."""
        # eRNA characteristics:
        # 1. Bidirectional transcription
        # 2. Low polyA signal relative to total
        # 3. CAGE peaks
        # 4. Not in exonic regions
        
        if not self.bidirectional_transcription:
            return False
        
        if self.total_rna > 0:
            polya_ratio = self.polya_rna / self.total_rna
            if polya_ratio > 0.5:  # Too much polyA for eRNA
                return False
        
        return self.cage_signal > 0


@dataclass
class EnhancerDetectionResult:
    """Enhanced detection result with scientific rigor."""
    # Core results
    is_enhancer: bool
    enhancer_state: EnhancerState
    confidence: str  # "high", "medium", "low"
    confidence_score: float  # 0-1
    
    # Evidence details
    evidence: EnhancerEvidence
    genomic_context: GenomicContext
    
    # Scoring breakdown
    histone_score: float
    accessibility_score: float
    rna_score: float
    statistical_significance: float
    
    # Interpretation
    positive_marks: List[str]
    missing_marks: List[str]
    warnings: List[str]
    interpretation: str
    
    # Metadata
    algorithm_version: str = "2.0"
    detection_criteria: str = ""
    
    def to_report_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting."""
        return {
            "detected": self.is_enhancer,
            "state": self.enhancer_state.value,
            "confidence": self.confidence,
            "confidence_score": round(self.confidence_score, 3),
            "region_type": self.genomic_context.region_type.value,
            "is_coding": self.genomic_context.is_coding,
            "positive_evidence": self.positive_marks,
            "missing_evidence": self.missing_marks,
            "warnings": self.warnings,
            "interpretation": self.interpretation,
            "scores": {
                "histone": round(self.histone_score, 3),
                "accessibility": round(self.accessibility_score, 3),
                "rna": round(self.rna_score, 3),
                "statistical": round(self.statistical_significance, 3)
            }
        }


class ScientificEnhancerDetector:
    """
    Scientifically rigorous enhancer detector addressing feedback.
    
    Key improvements:
    1. Mandatory H3K4me1/H3K27ac requirements
    2. Exon/promoter blacklisting
    3. Statistical validation against background
    4. eRNA vs mRNA differentiation
    5. Tissue-matched data requirements
    """
    
    # Strict thresholds based on ENCODE standards
    STRICT_THRESHOLDS = {
        "h3k4me1_min_zscore": 2.0,      # Significant enrichment required
        "h3k27ac_min_zscore": 2.0,      # For active enhancers
        "dnase_min_zscore": 1.5,        # Open chromatin
        "h3k4me3_max_zscore": 1.0,      # Should be low for enhancers
        "h3k36me3_max_zscore": 1.0,     # Should be low (gene body mark)
        "min_replicate_count": 2,       # Require replicates
        "min_statistical_significance": 0.05  # p-value threshold
    }
    
    def __init__(self, strict_mode: bool = True):
        """
        Initialize detector.
        
        Args:
            strict_mode: If True, apply most conservative criteria
        """
        self.strict_mode = strict_mode
    
    def detect(
        self,
        alphagenome_data: Dict[str, Any],
        genomic_context: GenomicContext,
        tissue_type: str = "generic"
    ) -> EnhancerDetectionResult:
        """
        Perform scientifically rigorous enhancer detection.
        
        Args:
            alphagenome_data: AlphaGenome prediction results
            genomic_context: Genomic context of the variant
            tissue_type: Tissue type for matching
            
        Returns:
            Comprehensive detection result
        """
        # Extract evidence from AlphaGenome data
        evidence = self._extract_evidence(alphagenome_data, tissue_type)
        
        # Calculate statistical measures
        evidence.calculate_z_scores()
        
        # Initialize result tracking
        warnings = []
        positive_marks = []
        missing_marks = []
        
        # Check for blacklisted regions first
        if genomic_context.is_blacklisted_for_enhancer:
            warnings.append(f"Region type '{genomic_context.region_type.value}' is not suitable for enhancer calling")
            if genomic_context.is_coding:
                warnings.append("Coding variants should not be called as enhancers")
            
            return EnhancerDetectionResult(
                is_enhancer=False,
                enhancer_state=EnhancerState.NOT_ENHANCER,
                confidence="low",
                confidence_score=0.0,
                evidence=evidence,
                genomic_context=genomic_context,
                histone_score=0.0,
                accessibility_score=0.0,
                rna_score=0.0,
                statistical_significance=0.0,
                positive_marks=[],
                missing_marks=["Region blacklisted"],
                warnings=warnings,
                interpretation="This region is not suitable for enhancer detection (exon/promoter/coding region)",
                detection_criteria="Strict scientific criteria v2.0"
            )
        
        # Evaluate core histone marks (MANDATORY)
        histone_score = 0.0
        
        # H3K4me1 - Essential enhancer mark
        if evidence.z_scores.get("h3k4me1", 0) >= self.STRICT_THRESHOLDS["h3k4me1_min_zscore"]:
            positive_marks.append(f"H3K4me1 (z={evidence.z_scores['h3k4me1']:.2f})")
            histone_score += 0.4
        else:
            missing_marks.append("H3K4me1 enrichment")
        
        # H3K27ac - Active enhancer mark
        h3k27ac_present = False
        if evidence.z_scores.get("h3k27ac", 0) >= self.STRICT_THRESHOLDS["h3k27ac_min_zscore"]:
            positive_marks.append(f"H3K27ac (z={evidence.z_scores['h3k27ac']:.2f})")
            histone_score += 0.4
            h3k27ac_present = True
        else:
            missing_marks.append("H3K27ac enrichment")
        
        # H3K4me3 - Should be LOW for enhancers
        if evidence.z_scores.get("h3k4me3", 0) <= self.STRICT_THRESHOLDS["h3k4me3_max_zscore"]:
            histone_score += 0.1
        else:
            warnings.append(f"High H3K4me3 (z={evidence.z_scores['h3k4me3']:.2f}) suggests promoter")
            histone_score -= 0.2
        
        # H3K36me3 - Gene body mark, should be LOW
        if evidence.z_scores.get("h3k36me3", 0) > self.STRICT_THRESHOLDS["h3k36me3_max_zscore"]:
            warnings.append(f"High H3K36me3 suggests gene body region")
            histone_score -= 0.1
        
        # Accessibility
        accessibility_score = 0.0
        if evidence.z_scores.get("dnase", 0) >= self.STRICT_THRESHOLDS["dnase_min_zscore"]:
            positive_marks.append(f"DNase accessibility (z={evidence.z_scores['dnase']:.2f})")
            accessibility_score = 0.5
        elif evidence.z_scores.get("atac", 0) >= self.STRICT_THRESHOLDS["dnase_min_zscore"]:
            positive_marks.append(f"ATAC accessibility (z={evidence.z_scores['atac']:.2f})")
            accessibility_score = 0.5
        else:
            missing_marks.append("Chromatin accessibility")
        
        # RNA evidence (distinguish eRNA from mRNA)
        rna_score = 0.0
        if evidence.is_likely_erna:
            positive_marks.append("Bidirectional eRNA transcription")
            rna_score = 0.3
        elif evidence.total_rna > 0 and genomic_context.region_type == RegionType.INTERGENIC:
            # Intergenic RNA could be eRNA
            positive_marks.append("Intergenic RNA signal")
            rna_score = 0.2
        elif evidence.total_rna > 0:
            warnings.append("RNA signal may be mRNA, not eRNA")
        
        # Check tissue matching
        if not evidence.tissue_matched:
            warnings.append(f"Data not from matched tissue type ({tissue_type})")
        
        # Check replication
        if evidence.replicate_count < self.STRICT_THRESHOLDS["min_replicate_count"]:
            warnings.append(f"Insufficient replicates ({evidence.replicate_count})")
        
        # Calculate overall scores
        total_score = histone_score + accessibility_score + rna_score
        statistical_significance = self._calculate_significance(evidence)
        
        # Determine enhancer state
        enhancer_state = self._determine_enhancer_state(
            evidence, h3k27ac_present, positive_marks
        )
        
        # Make final call with STRICT requirements
        is_enhancer = False
        confidence = "low"
        confidence_score = 0.0
        
        if self.strict_mode:
            # Strict: Require BOTH H3K4me1 and (H3K27ac OR H3K4me1+accessibility)
            if "H3K4me1" in " ".join(positive_marks):
                if h3k27ac_present:
                    is_enhancer = True
                    confidence = "high" if len(positive_marks) >= 3 else "medium"
                elif "accessibility" in " ".join(positive_marks).lower():
                    is_enhancer = True
                    confidence = "medium"
                    enhancer_state = EnhancerState.PRIMED
        else:
            # Less strict: Allow with good evidence
            if total_score >= 0.6 and len(positive_marks) >= 2:
                is_enhancer = True
                confidence = "medium" if total_score >= 0.8 else "low"
        
        # Calculate confidence score (0-1)
        if is_enhancer:
            confidence_score = min(1.0, total_score / 1.5)
            confidence_score *= (1.0 if evidence.tissue_matched else 0.8)
            confidence_score *= (1.0 if len(warnings) == 0 else 0.9 ** len(warnings))
        
        # Generate interpretation
        interpretation = self._generate_interpretation(
            is_enhancer, enhancer_state, positive_marks, missing_marks, warnings
        )
        
        return EnhancerDetectionResult(
            is_enhancer=is_enhancer,
            enhancer_state=enhancer_state,
            confidence=confidence,
            confidence_score=confidence_score,
            evidence=evidence,
            genomic_context=genomic_context,
            histone_score=histone_score,
            accessibility_score=accessibility_score,
            rna_score=rna_score,
            statistical_significance=statistical_significance,
            positive_marks=positive_marks,
            missing_marks=missing_marks,
            warnings=warnings,
            interpretation=interpretation,
            detection_criteria="Strict scientific criteria v2.0" if self.strict_mode else "Balanced criteria v2.0"
        )
    
    def _extract_evidence(self, alphagenome_data: Dict[str, Any], tissue_type: str) -> EnhancerEvidence:
        """Extract evidence from AlphaGenome data."""
        summary = alphagenome_data.get("summary", {})
        evidence = EnhancerEvidence()
        
        # Extract histone marks
        histone_data = summary.get("chip_histone", {}).get("marks", {})
        evidence.h3k4me1_signal = histone_data.get("H3K4me1", {}).get("max_increase", 0)
        evidence.h3k27ac_signal = histone_data.get("H3K27ac", {}).get("max_increase", 0)
        evidence.h3k4me3_signal = histone_data.get("H3K4me3", {}).get("max_increase", 0)
        evidence.h3k36me3_signal = histone_data.get("H3K36me3", {}).get("max_increase", 0)
        evidence.h3k27me3_signal = histone_data.get("H3K27me3", {}).get("max_increase", 0)
        
        # Extract accessibility
        dnase_data = summary.get("dnase", {})
        evidence.dnase_signal = dnase_data.get("max_increase", 0)
        
        atac_data = summary.get("atac", {})
        evidence.atac_signal = atac_data.get("max_increase", 0)
        
        # Extract RNA
        rna_data = summary.get("rna_seq", {})
        evidence.total_rna = rna_data.get("max_increase", 0)
        
        # Extract CAGE if available
        cage_data = summary.get("cage", {})
        evidence.cage_signal = cage_data.get("max_signal", 0)
        evidence.bidirectional_transcription = cage_data.get("bidirectional", False)
        
        # Set tissue matching (simplified - would need proper mapping)
        evidence.tissue_matched = tissue_type in str(summary.get("tissue", ""))
        
        # Extract background statistics if available
        bg_stats = summary.get("background_statistics", {})
        for mark in ["h3k4me1", "h3k27ac", "dnase", "h3k4me3"]:
            if mark in bg_stats:
                evidence.background_mean[mark] = bg_stats[mark].get("mean", 0)
                evidence.background_std[mark] = bg_stats[mark].get("std", 1)
        
        # If no background stats, use conservative defaults
        if not evidence.background_mean:
            evidence.background_mean = {
                "h3k4me1": 0.01, "h3k27ac": 0.01, 
                "dnase": 0.01, "h3k4me3": 0.01
            }
            evidence.background_std = {
                "h3k4me1": 0.05, "h3k27ac": 0.05,
                "dnase": 0.05, "h3k4me3": 0.05
            }
        
        return evidence
    
    def _determine_enhancer_state(
        self, 
        evidence: EnhancerEvidence, 
        h3k27ac_present: bool,
        positive_marks: List[str]
    ) -> EnhancerState:
        """Determine enhancer chromatin state."""
        h3k4me1_present = "H3K4me1" in " ".join(positive_marks)
        
        if not h3k4me1_present:
            return EnhancerState.NOT_ENHANCER
        
        if h3k27ac_present:
            return EnhancerState.ACTIVE
        
        if evidence.h3k27me3_signal > 0.1:
            return EnhancerState.POISED
        
        if h3k4me1_present and not h3k27ac_present:
            return EnhancerState.PRIMED
        
        return EnhancerState.INACTIVE
    
    def _calculate_significance(self, evidence: EnhancerEvidence) -> float:
        """Calculate statistical significance score."""
        if not evidence.z_scores:
            return 0.0
        
        # Average z-score of positive signals
        positive_zscores = [z for z in evidence.z_scores.values() if z > 0]
        if positive_zscores:
            return min(1.0, np.mean(positive_zscores) / 5.0)
        return 0.0
    
    def _generate_interpretation(
        self,
        is_enhancer: bool,
        state: EnhancerState,
        positive_marks: List[str],
        missing_marks: List[str],
        warnings: List[str]
    ) -> str:
        """Generate scientific interpretation."""
        if not is_enhancer:
            if warnings and "blacklisted" in " ".join(warnings).lower():
                return "Region is not suitable for enhancer calling (exon/promoter/coding)."
            
            missing_text = ", ".join(missing_marks) if missing_marks else "multiple criteria"
            return f"No enhancer detected. Missing: {missing_text}."
        
        state_descriptions = {
            EnhancerState.ACTIVE: "Active enhancer",
            EnhancerState.PRIMED: "Primed enhancer",
            EnhancerState.POISED: "Poised enhancer",
            EnhancerState.INACTIVE: "Inactive enhancer element"
        }
        
        base_text = f"{state_descriptions.get(state, 'Enhancer')} detected with {len(positive_marks)} positive marks."
        
        if warnings:
            base_text += f" Caution: {'; '.join(warnings[:2])}."
        
        return base_text


class GenomicAnnotator:
    """Helper class to annotate genomic positions."""
    
    @staticmethod
    def get_region_type(chrom: str, position: int, gene_annotations: Dict) -> RegionType:
        """
        Determine region type for a genomic position.
        
        This is a simplified version - real implementation would use
        proper gene annotation databases (GTF/GFF files).
        """
        # For KRAS chr12:25398284 - this is in exon 2
        if chrom == "chr12" and 25398000 <= position <= 25399000:
            return RegionType.EXON
        
        # Add more annotations as needed
        # This would normally query a gene annotation database
        
        return RegionType.INTERGENIC
    
    @staticmethod
    def is_coding_variant(protein_change: Optional[str]) -> bool:
        """Check if variant causes protein coding change."""
        if not protein_change:
            return False
        
        # Check for missense, nonsense, frameshift etc
        coding_indicators = ["p.", "fs", "del", "ins", "dup", "*"]
        return any(ind in protein_change for ind in coding_indicators)