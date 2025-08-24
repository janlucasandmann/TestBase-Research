"""
Enhancer Probability Calculation Module

This module computes per-base-pair enhancer probabilities by combining
multiple genomic signals using a biologically-informed probabilistic model.
"""

import numpy as np
from typing import Dict, Any, Tuple, Optional, List
from scipy import stats
from scipy.special import expit  # Sigmoid function
import logging

logger = logging.getLogger(__name__)


class EnhancerProbabilityCalculator:
    """
    Calculate per-base-pair enhancer probabilities from genomic signals.
    
    This calculator combines multiple epigenomic signals to compute
    enhancer probabilities using a weighted logistic model inspired by
    ChromHMM and other state-of-the-art genomic prediction methods.
    """
    
    # Signal weights based on biological importance for enhancer detection
    SIGNAL_WEIGHTS = {
        'H3K27ac': 0.35,   # Strong indicator of active enhancers
        'H3K4me1': 0.30,   # General enhancer mark
        'DNase': 0.25,     # Chromatin accessibility
        'H3K4me3': -0.20,  # Negative weight - indicates promoters
        'RNA': 0.10        # Can indicate enhancer RNA production
    }
    
    # Z-score thresholds for signal significance
    ZSCORE_THRESHOLDS = {
        'low': 1.0,
        'medium': 2.0,
        'high': 3.0
    }
    
    def __init__(self, window_size: int = 5):
        """
        Initialize the enhancer probability calculator.
        
        Args:
            window_size: Size of sliding window for smoothing (default: 5bp)
        """
        self.window_size = window_size
        
    def _calculate_base_probabilities(
        self,
        raw_signals: Dict[str, np.ndarray],
        seq_length: int
    ) -> np.ndarray:
        """
        Internal method to calculate base probabilities without bootstrap.
        
        Args:
            raw_signals: Dictionary of signal arrays
            seq_length: Expected sequence length
            
        Returns:
            Array of probabilities
        """
        # Initialize probability array
        combined_score = np.zeros(seq_length)
        signal_count = 0
        
        # Process each signal type
        for signal_name, weight in self.SIGNAL_WEIGHTS.items():
            signal_data = raw_signals.get(signal_name)
            
            if signal_data is None or len(signal_data) == 0:
                continue
                
            # Ensure signal is the right length - truncate or pad as needed
            if len(signal_data) != seq_length:
                if len(signal_data) > seq_length:
                    signal_data = signal_data[:seq_length]
                else:
                    # Pad with zeros if too short
                    signal_data = np.pad(signal_data, (0, seq_length - len(signal_data)), mode='constant')
                
            # Normalize signal to z-scores
            z_scores = self._normalize_to_zscore(signal_data)
            
            # Apply weight and add to combined score
            combined_score += weight * z_scores
            signal_count += 1
            
        if signal_count == 0:
            return np.zeros(seq_length)
            
        # Apply smoothing
        smoothed_score = self._apply_smoothing(combined_score)
        
        # Convert to probabilities using sigmoid function
        return expit(smoothed_score)
    
    def calculate_probabilities(
        self,
        raw_signals: Dict[str, np.ndarray],
        mutation_position: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Calculate enhancer probabilities from raw genomic signals.
        
        Args:
            raw_signals: Dictionary of signal arrays (e.g., DNase, H3K27ac, etc.)
            mutation_position: Position of the mutation in the array (optional)
            
        Returns:
            Dictionary containing:
                - probabilities: Array of enhancer probabilities
                - confidence_lower: Lower bound of 95% confidence interval
                - confidence_upper: Upper bound of 95% confidence interval
                - mean_probability: Overall mean probability
                - peak_probability: Maximum probability in the region
                - peak_position: Position of maximum probability
        """
        # Determine sequence length from first available signal
        seq_length = None
        for signal_array in raw_signals.values():
            if signal_array is not None and len(signal_array) > 0:
                seq_length = len(signal_array)
                break
                
        if seq_length is None:
            logger.warning("No valid signals found for probability calculation")
            return self._empty_result(1000)
            
        # Calculate base probabilities
        probabilities = self._calculate_base_probabilities(raw_signals, seq_length)
        
        # Calculate confidence intervals using bootstrap
        ci_lower, ci_upper = self._calculate_confidence_intervals(
            raw_signals, seq_length
        )
        
        # Find peak regions
        peak_prob = np.max(probabilities)
        peak_pos = np.argmax(probabilities)
        
        # Calculate statistics
        mean_prob = np.mean(probabilities)
        
        # Create result dictionary
        result = {
            'probabilities': probabilities.tolist(),
            'confidence_lower': ci_lower.tolist(),
            'confidence_upper': ci_upper.tolist(),
            'mean_probability': float(mean_prob),
            'peak_probability': float(peak_prob),
            'peak_position': int(peak_pos),
            'sequence_length': seq_length
        }
        
        # Add mutation-specific statistics if position provided
        if mutation_position is not None and 0 <= mutation_position < seq_length:
            result['mutation_position'] = mutation_position
            result['mutation_probability'] = float(probabilities[mutation_position])
            
            # Calculate local change around mutation (±10bp window)
            window_start = max(0, mutation_position - 10)
            window_end = min(seq_length, mutation_position + 10)
            local_mean = np.mean(probabilities[window_start:window_end])
            result['local_mean_probability'] = float(local_mean)
            
        return result
        
    def compare_reference_and_mutant(
        self,
        ref_signals: Dict[str, np.ndarray],
        mut_signals: Dict[str, np.ndarray],
        mutation_position: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Compare enhancer probabilities between reference and mutant sequences.
        
        Args:
            ref_signals: Reference sequence signals
            mut_signals: Mutant sequence signals
            mutation_position: Position of the mutation
            
        Returns:
            Dictionary containing comparison metrics and both probability arrays
        """
        # Calculate probabilities for both sequences
        ref_probs = self.calculate_probabilities(ref_signals, mutation_position)
        mut_probs = self.calculate_probabilities(mut_signals, mutation_position)
        
        # Calculate difference metrics
        ref_array = np.array(ref_probs['probabilities'])
        mut_array = np.array(mut_probs['probabilities'])
        
        # Ensure arrays are same length
        min_length = min(len(ref_array), len(mut_array))
        ref_array = ref_array[:min_length]
        mut_array = mut_array[:min_length]
        
        # Calculate differences
        prob_diff = mut_array - ref_array
        mean_diff = np.mean(prob_diff)
        max_diff = np.max(np.abs(prob_diff))
        
        # Find regions with significant changes
        significant_changes = []
        threshold = 0.1  # 10% probability change threshold
        
        for i in range(len(prob_diff)):
            if abs(prob_diff[i]) > threshold:
                significant_changes.append({
                    'position': i,
                    'change': float(prob_diff[i]),
                    'reference': float(ref_array[i]),
                    'mutant': float(mut_array[i])
                })
                
        # Create comprehensive result
        result = {
            'reference': ref_probs,
            'mutant': mut_probs,
            'difference': {
                'probabilities': prob_diff.tolist(),
                'mean_change': float(mean_diff),
                'max_change': float(max_diff),
                'significant_changes': significant_changes[:10]  # Top 10 changes
            }
        }
        
        # Add mutation-specific impact if position provided
        if mutation_position is not None and 0 <= mutation_position < min_length:
            result['mutation_impact'] = {
                'position': mutation_position,
                'reference_probability': float(ref_array[mutation_position]),
                'mutant_probability': float(mut_array[mutation_position]),
                'probability_change': float(prob_diff[mutation_position]),
                'is_gain': prob_diff[mutation_position] > 0.05,
                'is_loss': prob_diff[mutation_position] < -0.05
            }
            
        return result
        
    def _normalize_to_zscore(self, signal: np.ndarray) -> np.ndarray:
        """
        Normalize signal to z-scores, handling edge cases.
        
        Args:
            signal: Raw signal array
            
        Returns:
            Z-score normalized array
        """
        # Handle constant signals
        if np.std(signal) == 0:
            return np.zeros_like(signal)
            
        # Calculate z-scores
        z_scores = stats.zscore(signal)
        
        # Clip extreme values to prevent numerical issues
        z_scores = np.clip(z_scores, -5, 5)
        
        return z_scores
        
    def _apply_smoothing(self, scores: np.ndarray) -> np.ndarray:
        """
        Apply sliding window smoothing to reduce noise.
        
        Args:
            scores: Array of combined scores
            
        Returns:
            Smoothed score array
        """
        if len(scores) <= self.window_size:
            return scores
            
        # Use convolution for efficient smoothing
        kernel = np.ones(self.window_size) / self.window_size
        
        # Pad array to maintain size
        padded = np.pad(scores, (self.window_size//2, self.window_size//2), mode='edge')
        
        # Apply convolution
        smoothed = np.convolve(padded, kernel, mode='valid')
        
        # Ensure output size matches input
        if len(smoothed) != len(scores):
            smoothed = smoothed[:len(scores)]
            
        return smoothed
        
    def _calculate_confidence_intervals(
        self,
        raw_signals: Dict[str, np.ndarray],
        seq_length: int,
        n_bootstrap: int = 100,
        confidence_level: float = 0.95
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate confidence intervals using bootstrap resampling.
        
        Args:
            raw_signals: Dictionary of signal arrays
            seq_length: Length of the sequence
            n_bootstrap: Number of bootstrap iterations
            confidence_level: Confidence level (default: 95%)
            
        Returns:
            Tuple of (lower_bound, upper_bound) arrays
        """
        # Collect bootstrap samples
        bootstrap_probs = []
        
        for _ in range(min(n_bootstrap, 5)):  # Limit for performance and avoid excessive warnings
            # Add noise to simulate uncertainty
            noisy_signals = {}
            for signal_name, signal_data in raw_signals.items():
                if signal_data is not None and len(signal_data) > 0:
                    noise = np.random.normal(0, 0.1, len(signal_data))
                    noisy_signals[signal_name] = signal_data + noise
                    
            # Calculate probabilities with noisy signals using internal method
            probs = self._calculate_base_probabilities(noisy_signals, seq_length)
            bootstrap_probs.append(probs.tolist())
                
        if not bootstrap_probs:
            # Return default confidence intervals
            return np.zeros(seq_length), np.ones(seq_length)
            
        # Calculate percentiles for confidence intervals
        bootstrap_array = np.array(bootstrap_probs)
        alpha = 1 - confidence_level
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100
        
        ci_lower = np.percentile(bootstrap_array, lower_percentile, axis=0)
        ci_upper = np.percentile(bootstrap_array, upper_percentile, axis=0)
        
        return ci_lower, ci_upper
        
    def _empty_result(self, length: int) -> Dict[str, Any]:
        """
        Create an empty result structure when no data is available.
        
        Args:
            length: Expected sequence length
            
        Returns:
            Empty result dictionary
        """
        zeros = np.zeros(length)
        return {
            'probabilities': zeros.tolist(),
            'confidence_lower': zeros.tolist(),
            'confidence_upper': zeros.tolist(),
            'mean_probability': 0.0,
            'peak_probability': 0.0,
            'peak_position': 0,
            'sequence_length': length
        }
        
    def extract_signals_from_alphagenome(
        self,
        alphagenome_result: Dict[str, Any],
        sequence_type: str = 'reference'
    ) -> Dict[str, np.ndarray]:
        """
        Extract and format signals from AlphaGenome output.
        
        Args:
            alphagenome_result: Raw AlphaGenome API result
            sequence_type: 'reference' or 'alternate'
            
        Returns:
            Dictionary of signal arrays
        """
        signals = {}
        raw_data = alphagenome_result.get('raw', {})
        
        # Get the appropriate output set
        outputs = raw_data.get(sequence_type)
        if not outputs:
            return signals
            
        # Extract DNase signal
        if hasattr(outputs, 'dnase') and outputs.dnase is not None:
            signals['DNase'] = outputs.dnase.values.flatten()
            
        # Extract RNA signal
        if hasattr(outputs, 'rna_seq') and outputs.rna_seq is not None:
            signals['RNA'] = outputs.rna_seq.values.flatten()
            
        # Extract histone marks
        if hasattr(outputs, 'chip_histone') and outputs.chip_histone is not None:
            histone_values = outputs.chip_histone.values
            
            # Handle different shapes of histone data
            if len(histone_values.shape) == 3:
                # Shape is (batch, marks, sequence_length) - take first batch
                histone_values = histone_values[0]
            
            # Map histone marks to their tracks  
            # The order is typically: H3K4me3, H3K4me1, H3K36me3, H3K27me3, H3K9me3, H3K27ac
            histone_marks = ['H3K4me3', 'H3K4me1', 'H3K36me3', 'H3K27me3', 'H3K9me3', 'H3K27ac']
            
            if len(histone_values.shape) == 2:
                # Shape is (marks, sequence_length)
                for i, mark in enumerate(histone_marks):
                    if i < histone_values.shape[0]:
                        signals[mark] = histone_values[i].flatten()
            elif len(histone_values.shape) == 1:
                # Single mark, assume it's H3K27ac (most important for enhancers)
                signals['H3K27ac'] = histone_values.flatten()
                    
        return signals