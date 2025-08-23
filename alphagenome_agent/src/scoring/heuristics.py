"""Heuristics for computing delta values from AlphaGenome predictions."""

from typing import Dict, List, Optional

import numpy as np

from ..clients.alphagenome import AlphaGenomeResult
from ..core.logging import get_logger
from ..core.schemas import Modality

logger = get_logger(__name__)


def compute_modality_deltas(
    result: AlphaGenomeResult,
    methods: Optional[List[str]] = None
) -> Dict[str, float]:
    """Compute delta values for all tracks in an AlphaGenome result.
    
    Args:
        result: AlphaGenome prediction results
        methods: List of aggregation methods to use (default: ["mean"])
        
    Returns:
        Dictionary mapping track IDs to delta values
    """
    if methods is None:
        methods = ["mean"]
    
    deltas = {}
    
    for track_id in result.modality_data:
        for method in methods:
            try:
                delta = result.compute_delta(track_id, method)
                key = f"{track_id}_{method}" if len(methods) > 1 else track_id
                deltas[key] = delta
            except Exception as e:
                logger.warning(f"Failed to compute {method} delta for {track_id}: {e}")
                continue
    
    return deltas


def compute_peak_deltas(result: AlphaGenomeResult, window_size: int = 1000) -> Dict[str, float]:
    """Compute delta values focusing on peak regions.
    
    Args:
        result: AlphaGenome prediction results
        window_size: Size of window around peaks (bp)
        
    Returns:
        Dictionary mapping track IDs to peak delta values
    """
    deltas = {}
    
    for track_id, track_data in result.modality_data.items():
        ref_values = track_data.get("ref", np.array([]))
        alt_values = track_data.get("alt", np.array([]))
        
        if len(ref_values) == 0 or len(alt_values) == 0:
            continue
        
        try:
            # Find peaks in reference
            ref_peaks = find_peaks(ref_values)
            
            # Compute delta at peaks
            peak_deltas = []
            for peak_idx in ref_peaks:
                window_start = max(0, peak_idx - window_size // 2)
                window_end = min(len(ref_values), peak_idx + window_size // 2)
                
                ref_window = ref_values[window_start:window_end]
                alt_window = alt_values[window_start:window_end]
                
                if len(ref_window) > 0 and len(alt_window) > 0:
                    delta = np.mean(alt_window) - np.mean(ref_window)
                    peak_deltas.append(delta)
            
            if peak_deltas:
                deltas[f"{track_id}_peak"] = np.mean(peak_deltas)
        
        except Exception as e:
            logger.warning(f"Failed to compute peak delta for {track_id}: {e}")
            continue
    
    return deltas


def compute_positional_deltas(
    result: AlphaGenomeResult,
    positions: List[int]
) -> Dict[str, Dict[int, float]]:
    """Compute delta values at specific genomic positions.
    
    Args:
        result: AlphaGenome prediction results
        positions: List of genomic positions to query
        
    Returns:
        Nested dictionary: track_id -> position -> delta
    """
    positional_deltas = {}
    
    for track_id in result.modality_data:
        track_deltas = {}
        
        for pos in positions:
            try:
                delta = result.compute_delta_at_position(track_id, pos)
                track_deltas[pos] = delta
            except Exception as e:
                logger.warning(f"Failed to compute delta at position {pos} for {track_id}: {e}")
                continue
        
        if track_deltas:
            positional_deltas[track_id] = track_deltas
    
    return positional_deltas


def compute_auc_deltas(result: AlphaGenomeResult) -> Dict[str, float]:
    """Compute area-under-curve delta values.
    
    Args:
        result: AlphaGenome prediction results
        
    Returns:
        Dictionary mapping track IDs to AUC delta values
    """
    deltas = {}
    
    for track_id in result.modality_data:
        try:
            auc_delta = result.compute_auc_delta(track_id)
            deltas[f"{track_id}_auc"] = auc_delta
        except Exception as e:
            logger.warning(f"Failed to compute AUC delta for {track_id}: {e}")
            continue
    
    return deltas


def compute_percentile_deltas(
    result: AlphaGenomeResult,
    percentiles: List[float] = [50, 75, 90, 95]
) -> Dict[str, float]:
    """Compute delta values at various percentiles.
    
    Args:
        result: AlphaGenome prediction results
        percentiles: List of percentiles to compute (0-100)
        
    Returns:
        Dictionary mapping track_percentile to delta values
    """
    deltas = {}
    
    for track_id, track_data in result.modality_data.items():
        ref_values = track_data.get("ref", np.array([]))
        alt_values = track_data.get("alt", np.array([]))
        
        if len(ref_values) == 0 or len(alt_values) == 0:
            continue
        
        try:
            for pct in percentiles:
                ref_pct = np.percentile(ref_values, pct)
                alt_pct = np.percentile(alt_values, pct)
                delta = alt_pct - ref_pct
                
                deltas[f"{track_id}_p{int(pct)}"] = delta
        
        except Exception as e:
            logger.warning(f"Failed to compute percentile deltas for {track_id}: {e}")
            continue
    
    return deltas


def compute_modality_specific_deltas(result: AlphaGenomeResult) -> Dict[str, float]:
    """Compute deltas using modality-specific heuristics.
    
    Args:
        result: AlphaGenome prediction results
        
    Returns:
        Dictionary mapping track IDs to delta values
    """
    deltas = {}
    
    for track_id, track_data in result.modality_data.items():
        metadata = result.track_metadata.get(track_id, {})
        modality_str = metadata.get("modality", "")
        
        ref_values = track_data.get("ref", np.array([]))
        alt_values = track_data.get("alt", np.array([]))
        
        if len(ref_values) == 0 or len(alt_values) == 0:
            continue
        
        try:
            if modality_str == "TSS_CAGE":
                # For TSS/CAGE, focus on maximum values (peak activity)
                delta = np.max(alt_values) - np.max(ref_values)
            elif modality_str == "HISTONE":
                # For histones, use mean over top quartile
                ref_q75 = np.percentile(ref_values, 75)
                alt_q75 = np.percentile(alt_values, 75)
                ref_top = ref_values[ref_values >= ref_q75]
                alt_top = alt_values[alt_values >= alt_q75]
                
                if len(ref_top) > 0 and len(alt_top) > 0:
                    delta = np.mean(alt_top) - np.mean(ref_top)
                else:
                    delta = np.mean(alt_values) - np.mean(ref_values)
            elif modality_str == "ATAC_DNASE":
                # For accessibility, use AUC difference
                delta = result.compute_auc_delta(track_id)
            elif modality_str == "TF_BIND":
                # For TF binding, focus on peak differences
                delta = np.max(alt_values) - np.max(ref_values)
            else:
                # Default to mean difference
                delta = np.mean(alt_values) - np.mean(ref_values)
            
            deltas[track_id] = delta
        
        except Exception as e:
            logger.warning(f"Failed to compute modality-specific delta for {track_id}: {e}")
            continue
    
    return deltas


def find_peaks(values: np.ndarray, min_height: Optional[float] = None) -> List[int]:
    """Find peaks in a signal using simple local maxima detection.
    
    Args:
        values: Signal values
        min_height: Minimum height for peaks (default: 75th percentile)
        
    Returns:
        List of peak indices
    """
    if len(values) < 3:
        return []
    
    if min_height is None:
        min_height = np.percentile(values, 75)
    
    peaks = []
    
    # Simple peak detection: local maxima above threshold
    for i in range(1, len(values) - 1):
        if (values[i] > values[i-1] and 
            values[i] > values[i+1] and 
            values[i] >= min_height):
            peaks.append(i)
    
    return peaks


def compute_comprehensive_deltas(result: AlphaGenomeResult) -> Dict[str, float]:
    """Compute comprehensive set of delta measures.
    
    Args:
        result: AlphaGenome prediction results
        
    Returns:
        Dictionary with all computed delta measures
    """
    all_deltas = {}
    
    # Basic deltas
    basic_deltas = compute_modality_deltas(result, methods=["mean", "max", "min"])
    all_deltas.update(basic_deltas)
    
    # AUC deltas
    auc_deltas = compute_auc_deltas(result)
    all_deltas.update(auc_deltas)
    
    # Percentile deltas
    percentile_deltas = compute_percentile_deltas(result)
    all_deltas.update(percentile_deltas)
    
    # Peak deltas
    peak_deltas = compute_peak_deltas(result)
    all_deltas.update(peak_deltas)
    
    # Modality-specific deltas
    modality_deltas = compute_modality_specific_deltas(result)
    all_deltas.update({f"{k}_modality": v for k, v in modality_deltas.items()})
    
    return all_deltas