"""Comparison visualization functions for AlphaGenome results."""

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np

from ..clients.alphagenome import AlphaGenomeResult
from ..core.config import config
from ..core.logging import get_logger

logger = get_logger(__name__)


def create_comparison_plots(
    result: AlphaGenomeResult,
    title: str = "AlphaGenome Predictions Comparison"
) -> Optional[Path]:
    """Create a multi-panel comparison plot for all modalities.
    
    Args:
        result: AlphaGenome prediction results
        title: Plot title
        
    Returns:
        Path to saved figure, or None if creation failed
    """
    try:
        track_ids = list(result.modality_data.keys())
        if not track_ids:
            logger.warning("No tracks to plot")
            return None
        
        # Determine layout
        n_tracks = len(track_ids)
        if n_tracks <= 4:
            n_cols = 2
            n_rows = (n_tracks + 1) // 2
        else:
            n_cols = 3
            n_rows = (n_tracks + 2) // 3
        
        fig, axes = plt.subplots(
            n_rows, n_cols, 
            figsize=(n_cols * 6, n_rows * 3),
            squeeze=False
        )
        
        # Plot each track
        for i, track_id in enumerate(track_ids):
            row = i // n_cols
            col = i % n_cols
            ax = axes[row, col]
            
            try:
                plot_track_comparison(result, track_id, ax)
            except Exception as e:
                logger.warning(f"Failed to plot track {track_id}: {e}")
                ax.text(0.5, 0.5, f"Plot failed\n{track_id}", 
                       ha='center', va='center', transform=ax.transAxes)
        
        # Hide unused subplots
        for i in range(n_tracks, n_rows * n_cols):
            row = i // n_cols
            col = i % n_cols
            axes[row, col].set_visible(False)
        
        plt.suptitle(title, fontsize=14, y=0.98)
        plt.tight_layout()
        
        # Save figure
        config.ensure_directories()
        output_path = config.FIGURES_DIR / "alphagenome_comparison.png"
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        return output_path
        
    except Exception as e:
        logger.error(f"Failed to create comparison plot: {e}")
        return None


def plot_track_comparison(
    result: AlphaGenomeResult,
    track_id: str,
    ax: plt.Axes
) -> None:
    """Plot REF vs ALT comparison for a single track.
    
    Args:
        result: AlphaGenome prediction results
        track_id: Track identifier
        ax: Matplotlib axes to plot on
    """
    track_data = result.modality_data.get(track_id, {})
    ref_values = track_data.get("ref", np.array([]))
    alt_values = track_data.get("alt", np.array([]))
    
    if len(ref_values) == 0:
        ax.text(0.5, 0.5, "No data", ha='center', va='center', transform=ax.transAxes)
        ax.set_title(track_id)
        return
    
    # Use coordinates if available, otherwise use indices
    x_coords = result.coordinates[:len(ref_values)] if len(result.coordinates) >= len(ref_values) else np.arange(len(ref_values))
    
    # Plot REF and ALT
    ax.plot(x_coords, ref_values, label="REF", color='blue', alpha=0.7, linewidth=1)
    if len(alt_values) > 0:
        alt_x = result.coordinates[:len(alt_values)] if len(result.coordinates) >= len(alt_values) else np.arange(len(alt_values))
        ax.plot(alt_x, alt_values, label="ALT", color='red', alpha=0.7, linewidth=1)
    
    # Compute and display delta
    if len(alt_values) > 0:
        delta = result.compute_delta(track_id, "mean")
        ax.text(0.02, 0.98, f"Δ = {delta:.3f}", 
               transform=ax.transAxes, va='top', ha='left',
               bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    
    ax.set_title(track_id, fontsize=10)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    
    # Format x-axis for genomic coordinates
    if len(result.coordinates) > 0:
        ax.ticklabel_format(style='plain', axis='x')
        ax.set_xlabel("Position (bp)", fontsize=8)
    else:
        ax.set_xlabel("Index", fontsize=8)
    
    ax.set_ylabel("Signal", fontsize=8)


def create_delta_heatmap(
    results: List[AlphaGenomeResult],
    variant_labels: List[str],
    title: str = "Delta Heatmap"
) -> Optional[Path]:
    """Create a heatmap of delta values across variants and tracks.
    
    Args:
        results: List of AlphaGenome results
        variant_labels: Labels for each variant
        title: Plot title
        
    Returns:
        Path to saved figure, or None if creation failed
    """
    try:
        if not results:
            return None
        
        # Get all unique track IDs
        all_tracks = set()
        for result in results:
            all_tracks.update(result.modality_data.keys())
        
        if not all_tracks:
            return None
        
        track_list = sorted(all_tracks)
        
        # Create delta matrix
        delta_matrix = np.zeros((len(results), len(track_list)))
        
        for i, result in enumerate(results):
            for j, track_id in enumerate(track_list):
                try:
                    delta = result.compute_delta(track_id, "mean")
                    delta_matrix[i, j] = delta
                except:
                    delta_matrix[i, j] = 0.0
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(max(8, len(track_list) * 0.5), max(4, len(results) * 0.3)))
        
        im = ax.imshow(delta_matrix, cmap='RdBu_r', aspect='auto')
        
        # Set ticks and labels
        ax.set_xticks(range(len(track_list)))
        ax.set_xticklabels(track_list, rotation=45, ha='right', fontsize=8)
        ax.set_yticks(range(len(variant_labels)))
        ax.set_yticklabels(variant_labels, fontsize=8)
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label("Delta (ALT - REF)", fontsize=10)
        
        # Add value annotations for small matrices
        if len(results) <= 10 and len(track_list) <= 10:
            for i in range(len(results)):
                for j in range(len(track_list)):
                    text = ax.text(j, i, f"{delta_matrix[i, j]:.2f}",
                                 ha="center", va="center", color="black", fontsize=6)
        
        ax.set_title(title, fontsize=12)
        plt.tight_layout()
        
        # Save figure
        config.ensure_directories()
        output_path = config.FIGURES_DIR / "delta_heatmap.png"
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        return output_path
        
    except Exception as e:
        logger.error(f"Failed to create delta heatmap: {e}")
        return None


def create_modality_summary_plot(
    result: AlphaGenomeResult,
    title: str = "Modality Summary"
) -> Optional[Path]:
    """Create a summary plot showing delta values by modality.
    
    Args:
        result: AlphaGenome prediction results
        title: Plot title
        
    Returns:
        Path to saved figure, or None if creation failed
    """
    try:
        # Group tracks by modality
        modality_groups = {}
        
        for track_id in result.modality_data.keys():
            metadata = result.track_metadata.get(track_id, {})
            modality = metadata.get("modality", "Unknown")
            
            if modality not in modality_groups:
                modality_groups[modality] = []
            
            try:
                delta = result.compute_delta(track_id, "mean")
                modality_groups[modality].append((track_id, delta))
            except:
                continue
        
        if not modality_groups:
            return None
        
        # Create bar plot
        fig, ax = plt.subplots(figsize=(10, 6))
        
        modalities = list(modality_groups.keys())
        x_pos = np.arange(len(modalities))
        
        # Compute mean delta per modality
        mean_deltas = []
        error_bars = []
        
        for modality in modalities:
            deltas = [delta for _, delta in modality_groups[modality]]
            mean_deltas.append(np.mean(deltas))
            error_bars.append(np.std(deltas) if len(deltas) > 1 else 0)
        
        # Create bars
        bars = ax.bar(x_pos, mean_deltas, yerr=error_bars, 
                     capsize=5, alpha=0.7, color='steelblue')
        
        # Color bars by direction
        for i, (bar, delta) in enumerate(zip(bars, mean_deltas)):
            if delta > 0:
                bar.set_color('red')
            elif delta < 0:
                bar.set_color('blue')
        
        # Add value labels on bars
        for i, (bar, delta) in enumerate(zip(bars, mean_deltas)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + error_bars[i] + 0.01,
                   f'{delta:.3f}', ha='center', va='bottom', fontsize=9)
        
        ax.set_xlabel("Modality", fontsize=12)
        ax.set_ylabel("Mean Delta (ALT - REF)", fontsize=12)
        ax.set_title(title, fontsize=14)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(modalities, rotation=45, ha='right')
        ax.grid(True, alpha=0.3, axis='y')
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        plt.tight_layout()
        
        # Save figure
        config.ensure_directories()
        output_path = config.FIGURES_DIR / "modality_summary.png"
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        return output_path
        
    except Exception as e:
        logger.error(f"Failed to create modality summary plot: {e}")
        return None


def create_signal_overview(
    result: AlphaGenomeResult,
    title: str = "Signal Overview"
) -> Optional[Path]:
    """Create an overview plot showing all signals in a grid.
    
    Args:
        result: AlphaGenome prediction results
        title: Plot title
        
    Returns:
        Path to saved figure, or None if creation failed
    """
    try:
        track_ids = list(result.modality_data.keys())
        if not track_ids:
            return None
        
        # Create subplot grid
        n_tracks = len(track_ids)
        n_cols = min(3, n_tracks)
        n_rows = (n_tracks + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(
            n_rows, n_cols,
            figsize=(n_cols * 4, n_rows * 2.5),
            squeeze=False
        )
        
        for i, track_id in enumerate(track_ids):
            row = i // n_cols
            col = i % n_cols
            ax = axes[row, col]
            
            track_data = result.modality_data.get(track_id, {})
            ref_values = track_data.get("ref", np.array([]))
            alt_values = track_data.get("alt", np.array([]))
            
            if len(ref_values) > 0:
                x_coords = result.coordinates[:len(ref_values)] if len(result.coordinates) >= len(ref_values) else np.arange(len(ref_values))
                
                # Plot difference (ALT - REF)
                if len(alt_values) > 0:
                    delta_values = alt_values - ref_values
                    ax.plot(x_coords, delta_values, color='purple', linewidth=1)
                    ax.fill_between(x_coords, 0, delta_values, alpha=0.3, color='purple')
                else:
                    ax.plot(x_coords, ref_values, color='blue', linewidth=1)
                
                # Add zero line
                ax.axhline(y=0, color='black', linestyle='-', alpha=0.5, linewidth=0.5)
                
                # Compute stats
                if len(alt_values) > 0:
                    mean_delta = np.mean(alt_values) - np.mean(ref_values)
                    ax.text(0.02, 0.98, f"Δ = {mean_delta:.3f}", 
                           transform=ax.transAxes, va='top', ha='left', fontsize=8,
                           bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8))
            
            ax.set_title(track_id, fontsize=9)
            ax.grid(True, alpha=0.3)
            
            # Format axes
            if len(result.coordinates) > 0:
                ax.ticklabel_format(style='plain', axis='x')
            
            ax.tick_params(labelsize=8)
        
        # Hide unused subplots
        for i in range(n_tracks, n_rows * n_cols):
            row = i // n_cols
            col = i % n_cols
            axes[row, col].set_visible(False)
        
        plt.suptitle(title, fontsize=12, y=0.98)
        plt.tight_layout()
        
        # Save figure
        config.ensure_directories()
        output_path = config.FIGURES_DIR / "signal_overview.png"
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        return output_path
        
    except Exception as e:
        logger.error(f"Failed to create signal overview: {e}")
        return None