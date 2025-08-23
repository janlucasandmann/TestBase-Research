"""
Professional enhancer detection modules with literature-based criteria.

This module provides scientifically rigorous detection algorithms for regulatory elements
based on established chromatin marks and accessibility patterns.
"""

from __future__ import annotations
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


class DetectionAlgorithm(str, Enum):
    """Available detection algorithms."""
    CONSERVATIVE = "conservative"  # High specificity, lower sensitivity
    BALANCED = "balanced"         # Balanced specificity/sensitivity
    SENSITIVE = "sensitive"       # High sensitivity, lower specificity


class ConfidenceLevel(str, Enum):
    """Confidence levels for detection calls."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class DetectionCriteria:
    """Scientific criteria for regulatory element detection."""
    name: str
    description: str
    dnase_min_increase: float
    h3k27ac_min_increase: float
    h3k4me1_min_increase: float
    h3k4me3_min_increase: float
    rna_min_increase: float
    min_marks_required: int
    confidence_thresholds: Dict[str, int]  # marks required for each confidence level


@dataclass
class DetectionResult:
    """Result of regulatory element detection."""
    is_detected: bool
    confidence: ConfidenceLevel
    algorithm_used: DetectionAlgorithm
    criteria_used: str
    positive_marks: List[str]
    evidence_scores: Dict[str, float]
    total_evidence_score: float
    interpretation: str


class BaseDetector(ABC):
    """Base class for regulatory element detectors."""
    
    @abstractmethod
    def detect(self, alphagenome_summary: Dict[str, Any]) -> DetectionResult:
        """Detect regulatory elements from AlphaGenome summary data."""
        pass
    
    @abstractmethod
    def get_criteria_name(self) -> str:
        """Get the name of the detection criteria."""
        pass


class EnhancerDetector(BaseDetector):
    """
    Professional enhancer detection based on chromatin signatures.
    
    Based on established literature criteria:
    - Ernst & Kellis (2012) Nature
    - ENCODE Consortium (2012) Nature  
    - Roadmap Epigenomics Consortium (2015) Nature
    """
    
    # Literature-based detection criteria
    CRITERIA = {
        "conservative": DetectionCriteria(
            name="Conservative Enhancer Detection",
            description="High specificity criteria based on ENCODE standards",
            dnase_min_increase=0.05,    # Strong accessibility increase
            h3k27ac_min_increase=0.2,   # Strong active enhancer mark
            h3k4me1_min_increase=0.1,   # Strong enhancer mark
            h3k4me3_min_increase=-0.05, # Should not increase (promoter mark)
            rna_min_increase=0.001,     # Modest transcriptional effect
            min_marks_required=3,       # Require strong multi-mark evidence
            confidence_thresholds={"high": 4, "medium": 3, "low": 2}
        ),
        
        "balanced": DetectionCriteria(
            name="Balanced Enhancer Detection", 
            description="Balanced sensitivity/specificity for general use",
            dnase_min_increase=0.02,    # Moderate accessibility increase
            h3k27ac_min_increase=0.1,   # Moderate active enhancer mark
            h3k4me1_min_increase=0.05,  # Moderate enhancer mark
            h3k4me3_min_increase=0.0,   # No strong promoter signal
            rna_min_increase=0.0005,    # Small transcriptional effect
            min_marks_required=2,       # Require moderate evidence
            confidence_thresholds={"high": 3, "medium": 2, "low": 1}
        ),
        
        "sensitive": DetectionCriteria(
            name="Sensitive Enhancer Detection",
            description="High sensitivity for discovery applications", 
            dnase_min_increase=0.01,    # Small accessibility increase
            h3k27ac_min_increase=0.05,  # Small active enhancer mark
            h3k4me1_min_increase=0.02,  # Small enhancer mark
            h3k4me3_min_increase=0.05,  # Allow some promoter signal
            rna_min_increase=0.0001,    # Very small transcriptional effect
            min_marks_required=1,       # Single mark sufficient
            confidence_thresholds={"high": 3, "medium": 2, "low": 1}
        )
    }
    
    # Tissue-specific adjustment factors (based on tissue-specific chromatin states)
    TISSUE_ADJUSTMENTS = {
        "UBERON:0000310": {"factor": 1.0, "name": "breast"},        # Breast
        "UBERON:0001264": {"factor": 1.2, "name": "pancreatic"},    # Pancreas (higher threshold)
        "UBERON:0002048": {"factor": 0.9, "name": "lung"},          # Lung (lower threshold)
        "UBERON:0001157": {"factor": 1.1, "name": "colorectal"},    # Colon (slightly higher)
        "UBERON:0000955": {"factor": 1.3, "name": "brain"},         # Brain (much higher threshold)
        "UBERON:0002367": {"factor": 1.0, "name": "prostate"},      # Prostate
    }
    
    def __init__(self, algorithm: DetectionAlgorithm = DetectionAlgorithm.BALANCED):
        """Initialize enhancer detector with specified algorithm."""
        self.algorithm = algorithm
        self.criteria = self.CRITERIA[algorithm.value]
    
    def detect(self, alphagenome_summary: Dict[str, Any], tissue_id: Optional[str] = None) -> DetectionResult:
        """
        Detect enhancer-like regulatory elements.
        
        Args:
            alphagenome_summary: AlphaGenome API summary data
            tissue_id: Optional tissue ontology ID for tissue-specific thresholds
            
        Returns:
            DetectionResult with enhancer call and evidence
        """
        # Apply tissue-specific adjustments
        adjusted_criteria = self._apply_tissue_adjustments(tissue_id)
        
        # Extract signals from AlphaGenome summary
        signals = self._extract_signals(alphagenome_summary)
        
        # Test each mark against criteria
        positive_marks = []
        evidence_scores = {}
        
        # DNase accessibility (open chromatin)
        dnase_score = signals.get("dnase_increase", 0)
        if dnase_score >= adjusted_criteria.dnase_min_increase:
            positive_marks.append("DNase_accessibility")
            evidence_scores["dnase"] = self._calculate_evidence_score(
                dnase_score, adjusted_criteria.dnase_min_increase
            )
        
        # H3K27ac (active enhancer mark)
        h3k27ac_score = signals.get("h3k27ac_increase", 0)
        if h3k27ac_score >= adjusted_criteria.h3k27ac_min_increase:
            positive_marks.append("H3K27ac_active_enhancer")
            evidence_scores["h3k27ac"] = self._calculate_evidence_score(
                h3k27ac_score, adjusted_criteria.h3k27ac_min_increase
            )
        
        # H3K4me1 (enhancer mark)
        h3k4me1_score = signals.get("h3k4me1_increase", 0)
        if h3k4me1_score >= adjusted_criteria.h3k4me1_min_increase:
            positive_marks.append("H3K4me1_enhancer")
            evidence_scores["h3k4me1"] = self._calculate_evidence_score(
                h3k4me1_score, adjusted_criteria.h3k4me1_min_increase
            )
        
        # H3K4me3 (promoter mark - should not be too high for enhancers)
        h3k4me3_score = signals.get("h3k4me3_increase", 0)
        if h3k4me3_score < adjusted_criteria.h3k4me3_min_increase:
            # For enhancers, we want low H3K4me3 (this is good)
            evidence_scores["h3k4me3_low"] = 1.0
        elif h3k4me3_score > adjusted_criteria.h3k4me3_min_increase + 0.1:
            # High H3K4me3 suggests promoter, reduces enhancer confidence
            evidence_scores["h3k4me3_high"] = -0.5
        
        # RNA expression (enhancer transcription)
        rna_score = signals.get("rna_increase", 0)
        if rna_score >= adjusted_criteria.rna_min_increase:
            positive_marks.append("RNA_enhancer_transcription")
            evidence_scores["rna"] = self._calculate_evidence_score(
                rna_score, adjusted_criteria.rna_min_increase
            )
        
        # Make detection call
        is_detected = len(positive_marks) >= adjusted_criteria.min_marks_required
        
        # Calculate confidence
        confidence = self._calculate_confidence(len(positive_marks), adjusted_criteria)
        
        # Calculate total evidence score
        total_score = sum(score for score in evidence_scores.values() if score > 0)
        
        # Generate interpretation
        interpretation = self._generate_interpretation(
            is_detected, positive_marks, confidence, tissue_id
        )
        
        return DetectionResult(
            is_detected=is_detected,
            confidence=confidence,
            algorithm_used=self.algorithm,
            criteria_used=adjusted_criteria.name,
            positive_marks=positive_marks,
            evidence_scores=evidence_scores,
            total_evidence_score=total_score,
            interpretation=interpretation
        )
    
    def _apply_tissue_adjustments(self, tissue_id: Optional[str]) -> DetectionCriteria:
        """Apply tissue-specific threshold adjustments."""
        if not tissue_id or tissue_id not in self.TISSUE_ADJUSTMENTS:
            return self.criteria
        
        adjustment = self.TISSUE_ADJUSTMENTS[tissue_id]
        factor = adjustment["factor"]
        
        # Create adjusted criteria
        return DetectionCriteria(
            name=f"{self.criteria.name} ({adjustment['name']} tissue)",
            description=f"{self.criteria.description} with {adjustment['name']}-specific thresholds",
            dnase_min_increase=self.criteria.dnase_min_increase * factor,
            h3k27ac_min_increase=self.criteria.h3k27ac_min_increase * factor,
            h3k4me1_min_increase=self.criteria.h3k4me1_min_increase * factor,
            h3k4me3_min_increase=self.criteria.h3k4me3_min_increase,  # Don't adjust negative thresholds
            rna_min_increase=self.criteria.rna_min_increase * factor,
            min_marks_required=self.criteria.min_marks_required,
            confidence_thresholds=self.criteria.confidence_thresholds
        )
    
    def _extract_signals(self, summary: Dict[str, Any]) -> Dict[str, float]:
        """Extract relevant signals from AlphaGenome summary."""
        signals = {}
        
        # DNase accessibility
        dnase_data = summary.get("dnase", {})
        signals["dnase_increase"] = dnase_data.get("max_increase", 0)
        
        # Histone marks
        histone_data = summary.get("chip_histone", {}).get("marks", {})
        
        signals["h3k27ac_increase"] = histone_data.get("H3K27ac", {}).get("max_increase", 0)
        signals["h3k4me1_increase"] = histone_data.get("H3K4me1", {}).get("max_increase", 0) 
        signals["h3k4me3_increase"] = histone_data.get("H3K4me3", {}).get("max_increase", 0)
        
        # RNA expression
        rna_data = summary.get("rna_seq", {})
        signals["rna_increase"] = rna_data.get("max_increase", 0)
        
        return signals
    
    def _calculate_evidence_score(self, observed: float, threshold: float) -> float:
        """Calculate evidence score based on how much signal exceeds threshold."""
        if observed <= threshold:
            return 0.0
        
        # Score increases logarithmically with signal strength
        fold_increase = observed / threshold
        return min(math.log2(fold_increase + 1), 5.0)  # Cap at 5.0
    
    def _calculate_confidence(self, positive_marks: int, criteria: DetectionCriteria) -> ConfidenceLevel:
        """Calculate confidence level based on number of positive marks."""
        thresholds = criteria.confidence_thresholds
        
        if positive_marks >= thresholds["high"]:
            return ConfidenceLevel.HIGH
        elif positive_marks >= thresholds["medium"]:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
    
    def _generate_interpretation(
        self, 
        is_detected: bool, 
        positive_marks: List[str], 
        confidence: ConfidenceLevel,
        tissue_id: Optional[str]
    ) -> str:
        """Generate human-readable interpretation of results."""
        tissue_name = ""
        if tissue_id and tissue_id in self.TISSUE_ADJUSTMENTS:
            tissue_name = f" in {self.TISSUE_ADJUSTMENTS[tissue_id]['name']} tissue"
        
        if not is_detected:
            return f"No enhancer-like regulatory activity detected{tissue_name}. Insufficient chromatin signature evidence."
        
        mark_descriptions = {
            "DNase_accessibility": "open chromatin",
            "H3K27ac_active_enhancer": "active enhancer marks",
            "H3K4me1_enhancer": "enhancer chromatin state",
            "RNA_enhancer_transcription": "enhancer transcription"
        }
        
        evidence_list = [mark_descriptions.get(mark, mark) for mark in positive_marks]
        evidence_text = ", ".join(evidence_list)
        
        return (f"Enhancer-like regulatory activity detected{tissue_name} "
               f"({confidence.value} confidence). Evidence: {evidence_text}.")
    
    def get_criteria_name(self) -> str:
        """Get the name of the detection criteria."""
        return self.criteria.name


class PromoterDetector(BaseDetector):
    """
    Promoter detection based on chromatin signatures.
    
    Based on established criteria for active promoters:
    - High H3K4me3 (promoter mark)
    - DNase accessibility 
    - RNA polymerase II binding
    - Low H3K27me3 (repressive mark)
    """
    
    CRITERIA = {
        "conservative": DetectionCriteria(
            name="Conservative Promoter Detection",
            description="High specificity promoter detection",
            dnase_min_increase=0.05,    # Strong accessibility
            h3k27ac_min_increase=0.05,  # Some enhancer activity OK
            h3k4me1_min_increase=0.0,   # H3K4me1 not critical for promoters
            h3k4me3_min_increase=0.2,   # Strong promoter mark required
            rna_min_increase=0.002,     # Strong transcriptional effect
            min_marks_required=2,       # H3K4me3 + one other
            confidence_thresholds={"high": 3, "medium": 2, "low": 1}
        ),
        
        "balanced": DetectionCriteria(
            name="Balanced Promoter Detection",
            description="Balanced promoter detection",
            dnase_min_increase=0.02,
            h3k27ac_min_increase=0.02,
            h3k4me1_min_increase=0.0,
            h3k4me3_min_increase=0.1,
            rna_min_increase=0.001,
            min_marks_required=2,
            confidence_thresholds={"high": 3, "medium": 2, "low": 1}
        )
    }
    
    def __init__(self, algorithm: DetectionAlgorithm = DetectionAlgorithm.BALANCED):
        """Initialize promoter detector."""
        available_algorithms = ["conservative", "balanced"]
        if algorithm.value not in available_algorithms:
            algorithm = DetectionAlgorithm.BALANCED
            
        self.algorithm = algorithm
        self.criteria = self.CRITERIA[algorithm.value]
    
    def detect(self, alphagenome_summary: Dict[str, Any]) -> DetectionResult:
        """Detect promoter-like regulatory elements."""
        signals = self._extract_signals(alphagenome_summary)
        positive_marks = []
        evidence_scores = {}
        
        # H3K4me3 (promoter mark) - most important
        h3k4me3_score = signals.get("h3k4me3_increase", 0)
        if h3k4me3_score >= self.criteria.h3k4me3_min_increase:
            positive_marks.append("H3K4me3_promoter")
            evidence_scores["h3k4me3"] = h3k4me3_score / self.criteria.h3k4me3_min_increase
        
        # DNase accessibility
        dnase_score = signals.get("dnase_increase", 0)
        if dnase_score >= self.criteria.dnase_min_increase:
            positive_marks.append("DNase_accessibility")
            evidence_scores["dnase"] = dnase_score / self.criteria.dnase_min_increase
        
        # RNA expression
        rna_score = signals.get("rna_increase", 0)
        if rna_score >= self.criteria.rna_min_increase:
            positive_marks.append("RNA_transcription")
            evidence_scores["rna"] = rna_score / self.criteria.rna_min_increase
        
        is_detected = len(positive_marks) >= self.criteria.min_marks_required
        confidence = self._calculate_confidence(len(positive_marks))
        total_score = sum(evidence_scores.values())
        
        interpretation = self._generate_interpretation(is_detected, positive_marks, confidence)
        
        return DetectionResult(
            is_detected=is_detected,
            confidence=confidence,
            algorithm_used=self.algorithm,
            criteria_used=self.criteria.name,
            positive_marks=positive_marks,
            evidence_scores=evidence_scores,
            total_evidence_score=total_score,
            interpretation=interpretation
        )
    
    def _extract_signals(self, summary: Dict[str, Any]) -> Dict[str, float]:
        """Extract promoter-relevant signals."""
        signals = {}
        
        dnase_data = summary.get("dnase", {})
        signals["dnase_increase"] = dnase_data.get("max_increase", 0)
        
        histone_data = summary.get("chip_histone", {}).get("marks", {})
        signals["h3k4me3_increase"] = histone_data.get("H3K4me3", {}).get("max_increase", 0)
        
        rna_data = summary.get("rna_seq", {})
        signals["rna_increase"] = rna_data.get("max_increase", 0)
        
        return signals
    
    def _calculate_confidence(self, positive_marks: int) -> ConfidenceLevel:
        """Calculate confidence for promoter detection."""
        if positive_marks >= 3:
            return ConfidenceLevel.HIGH
        elif positive_marks >= 2:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
    
    def _generate_interpretation(self, is_detected: bool, positive_marks: List[str], confidence: ConfidenceLevel) -> str:
        """Generate promoter interpretation."""
        if not is_detected:
            return "No promoter-like regulatory activity detected."
        
        return f"Promoter-like regulatory activity detected ({confidence.value} confidence)."
    
    def get_criteria_name(self) -> str:
        """Get the name of the detection criteria."""
        return self.criteria.name


class DetectorFactory:
    """Factory for creating regulatory element detectors."""
    
    @staticmethod
    def create_enhancer_detector(algorithm: DetectionAlgorithm = DetectionAlgorithm.BALANCED) -> EnhancerDetector:
        """Create an enhancer detector with specified algorithm."""
        return EnhancerDetector(algorithm)
    
    @staticmethod
    def create_promoter_detector(algorithm: DetectionAlgorithm = DetectionAlgorithm.BALANCED) -> PromoterDetector:
        """Create a promoter detector with specified algorithm."""
        return PromoterDetector(algorithm)
    
    @staticmethod
    def get_available_algorithms() -> List[DetectionAlgorithm]:
        """Get list of available detection algorithms."""
        return list(DetectionAlgorithm)
    
    @staticmethod
    def get_algorithm_description(algorithm: DetectionAlgorithm) -> str:
        """Get description of detection algorithm."""
        descriptions = {
            DetectionAlgorithm.CONSERVATIVE: "High specificity, low false positive rate",
            DetectionAlgorithm.BALANCED: "Balanced sensitivity and specificity",
            DetectionAlgorithm.SENSITIVE: "High sensitivity, may have more false positives"
        }
        return descriptions.get(algorithm, "Unknown algorithm")