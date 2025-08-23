"""Score aggregation functions for combining delta values across modalities."""

from typing import Dict, List, Optional

import numpy as np

from ..core.logging import get_logger
from ..core.schemas import Modality

logger = get_logger(__name__)


def aggregate_scores(
    modality_deltas: Dict[str, float],
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, float]:
    """Aggregate delta scores using various methods.
    
    Args:
        modality_deltas: Dictionary of track_id -> delta values
        weights: Optional weights for each track
        
    Returns:
        Dictionary of aggregated scores
    """
    if not modality_deltas:
        return {}
    
    values = list(modality_deltas.values())
    
    # Basic aggregations
    scores = {
        "mean_delta": np.mean(values),
        "max_delta": np.max(values),
        "min_delta": np.min(values),
        "max_abs_delta": np.max(np.abs(values)),
        "sum_delta": np.sum(values),
        "std_delta": np.std(values) if len(values) > 1 else 0.0,
        "count_positive": sum(1 for v in values if v > 0),
        "count_negative": sum(1 for v in values if v < 0),
        "count_significant": sum(1 for v in values if abs(v) > 0.1)
    }
    
    # Weighted aggregations if weights provided
    if weights:
        weighted_values = []
        total_weight = 0
        
        for track_id, delta in modality_deltas.items():
            weight = weights.get(track_id, 1.0)
            weighted_values.append(delta * weight)
            total_weight += weight
        
        if total_weight > 0:
            scores["weighted_mean"] = np.sum(weighted_values) / total_weight
            scores["weighted_sum"] = np.sum(weighted_values)
    
    # Modality-specific aggregations
    modality_scores = aggregate_by_modality(modality_deltas)
    scores.update(modality_scores)
    
    return scores


def aggregate_by_modality(modality_deltas: Dict[str, float]) -> Dict[str, float]:
    """Aggregate deltas by modality type.
    
    Args:
        modality_deltas: Dictionary of track_id -> delta values
        
    Returns:
        Dictionary of modality-specific scores
    """
    # Group deltas by modality
    modality_groups = {
        "tss_cage": [],
        "histone": [],
        "atac_dnase": [],
        "tf_bind": [],
        "other": []
    }
    
    for track_id, delta in modality_deltas.items():
        # Simple heuristic to categorize tracks by name
        track_lower = track_id.lower()
        
        if "cage" in track_lower or "tss" in track_lower:
            modality_groups["tss_cage"].append(delta)
        elif any(mark in track_lower for mark in ["h3k", "histone", "k27ac", "k4me3"]):
            modality_groups["histone"].append(delta)
        elif "atac" in track_lower or "dnase" in track_lower:
            modality_groups["atac_dnase"].append(delta)
        elif any(tf in track_lower for tf in ["ctcf", "pol2", "bind", "tf_"]):
            modality_groups["tf_bind"].append(delta)
        else:
            modality_groups["other"].append(delta)
    
    # Aggregate each modality group
    scores = {}
    for modality, deltas in modality_groups.items():
        if deltas:
            scores[f"{modality}_mean"] = np.mean(deltas)
            scores[f"{modality}_max"] = np.max(deltas)
            scores[f"{modality}_count"] = len(deltas)
            scores[f"{modality}_max_abs"] = np.max(np.abs(deltas))
    
    return scores


def compute_regulatory_score(modality_deltas: Dict[str, float]) -> float:
    """Compute overall regulatory impact score.
    
    Args:
        modality_deltas: Dictionary of track_id -> delta values
        
    Returns:
        Overall regulatory score (higher = more regulatory impact)
    """
    if not modality_deltas:
        return 0.0
    
    # Weight different modalities based on regulatory importance
    weights = {
        "tss_cage": 1.5,      # Promoter activity is highly important
        "histone": 1.2,       # Histone marks are important regulatory signals
        "atac_dnase": 1.0,    # Accessibility is important but less specific
        "tf_bind": 0.8        # TF binding is important but context-dependent
    }
    
    weighted_deltas = []
    
    for track_id, delta in modality_deltas.items():
        track_lower = track_id.lower()
        
        # Determine modality and apply weight
        weight = 1.0  # default
        if "cage" in track_lower or "tss" in track_lower:
            weight = weights["tss_cage"]
        elif any(mark in track_lower for mark in ["h3k", "histone", "k27ac", "k4me3"]):
            weight = weights["histone"]
        elif "atac" in track_lower or "dnase" in track_lower:
            weight = weights["atac_dnase"]
        elif any(tf in track_lower for tf in ["ctcf", "pol2", "bind", "tf_"]):
            weight = weights["tf_bind"]
        
        weighted_deltas.append(abs(delta) * weight)
    
    if not weighted_deltas:
        return 0.0
    
    # Combine weighted absolute deltas
    return np.mean(weighted_deltas)


def compute_direction_consensus(modality_deltas: Dict[str, float]) -> Dict[str, float]:
    """Compute consensus direction and strength across modalities.
    
    Args:
        modality_deltas: Dictionary of track_id -> delta values
        
    Returns:
        Dictionary with direction consensus metrics
    """
    if not modality_deltas:
        return {}
    
    values = list(modality_deltas.values())
    
    positive_count = sum(1 for v in values if v > 0)
    negative_count = sum(1 for v in values if v < 0)
    total_count = len(values)
    
    # Direction consensus (0 = mixed, 1 = all same direction)
    consensus = max(positive_count, negative_count) / total_count
    
    # Overall direction (-1 = down, 0 = mixed, 1 = up)
    if positive_count > negative_count:
        direction = 1.0
    elif negative_count > positive_count:
        direction = -1.0
    else:
        direction = 0.0
    
    return {
        "direction_consensus": consensus,
        "overall_direction": direction,
        "positive_ratio": positive_count / total_count,
        "negative_ratio": negative_count / total_count
    }


def rank_tracks_by_impact(modality_deltas: Dict[str, float]) -> List[tuple]:
    """Rank tracks by their regulatory impact.
    
    Args:
        modality_deltas: Dictionary of track_id -> delta values
        
    Returns:
        List of (track_id, delta, abs_delta) tuples sorted by impact
    """
    ranked = [
        (track_id, delta, abs(delta))
        for track_id, delta in modality_deltas.items()
    ]
    
    # Sort by absolute delta (impact magnitude)
    ranked.sort(key=lambda x: x[2], reverse=True)
    
    return ranked


def compute_modality_balance(modality_deltas: Dict[str, float]) -> Dict[str, float]:
    """Compute balance scores across different modality types.
    
    Args:
        modality_deltas: Dictionary of track_id -> delta values
        
    Returns:
        Dictionary with modality balance metrics
    """
    # Group by modality
    modality_groups = {
        "promoter": [],    # TSS/CAGE + H3K4me3
        "enhancer": [],    # H3K27ac
        "accessibility": [], # ATAC/DNase
        "binding": []      # TF binding
    }
    
    for track_id, delta in modality_deltas.items():
        track_lower = track_id.lower()
        
        if "cage" in track_lower or "tss" in track_lower or "k4me3" in track_lower:
            modality_groups["promoter"].append(abs(delta))
        elif "k27ac" in track_lower:
            modality_groups["enhancer"].append(abs(delta))
        elif "atac" in track_lower or "dnase" in track_lower:
            modality_groups["accessibility"].append(abs(delta))
        elif any(tf in track_lower for tf in ["ctcf", "pol2", "bind", "tf_"]):
            modality_groups["binding"].append(abs(delta))
    
    # Compute balance metrics
    balance_scores = {}
    
    # Mean impact per modality
    for modality, deltas in modality_groups.items():
        if deltas:
            balance_scores[f"{modality}_impact"] = np.mean(deltas)
        else:
            balance_scores[f"{modality}_impact"] = 0.0
    
    # Overall balance (entropy-like measure)
    impacts = [balance_scores.get(f"{m}_impact", 0) for m in modality_groups.keys()]
    total_impact = sum(impacts)
    
    if total_impact > 0:
        proportions = [i / total_impact for i in impacts]
        # Compute entropy (higher = more balanced)
        entropy = -sum(p * np.log(p + 1e-10) for p in proportions if p > 0)
        balance_scores["modality_entropy"] = entropy / np.log(4)  # Normalize by max entropy
    else:
        balance_scores["modality_entropy"] = 0.0
    
    return balance_scores


def aggregate_comprehensive_scores(modality_deltas: Dict[str, float]) -> Dict[str, float]:
    """Compute comprehensive aggregated scores.
    
    Args:
        modality_deltas: Dictionary of track_id -> delta values
        
    Returns:
        Dictionary with all aggregated scores
    """
    all_scores = {}
    
    # Basic aggregations
    basic_scores = aggregate_scores(modality_deltas)
    all_scores.update(basic_scores)
    
    # Regulatory score
    all_scores["regulatory_score"] = compute_regulatory_score(modality_deltas)
    
    # Direction consensus
    direction_scores = compute_direction_consensus(modality_deltas)
    all_scores.update(direction_scores)
    
    # Modality balance
    balance_scores = compute_modality_balance(modality_deltas)
    all_scores.update(balance_scores)
    
    return all_scores