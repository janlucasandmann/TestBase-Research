# =============================================
# File: src/viz/tracks.py  
# =============================================
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
from datetime import datetime


def save_track(values: Iterable[float], *, title: str, xlabel: str = "position (bp)", dpi: int = 150, output_dir: Optional[Path] = None) -> Path:
    """Save a single track figure and return the image path."""
    values = np.asarray(list(values), dtype=float)
    fig, ax = plt.subplots(figsize=(8, 2.2))
    ax.plot(values)  # default color only
    ax.set_title(title, fontsize=10)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("signal")
    ax.grid(True, linewidth=0.3)
    fig.tight_layout()
    out = output_dir or Path("data/outputs/figures")
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{title.lower().replace(' ', '_')}.png"
    fig.savefig(path, dpi=dpi)
    plt.close(fig)
    return path


def save_ref_alt_delta(ref: Iterable[float], alt: Iterable[float], *, base_title: str) -> Tuple[Path, Path, Path]:
    """Helper to save REF, ALT and Δ(ALT-REF) figures for a modality."""
    ref = np.asarray(list(ref), dtype=float)
    alt = np.asarray(list(alt), dtype=float)
    delta = alt - ref
    p1 = save_track(ref, title=f"{base_title} REF")
    p2 = save_track(alt, title=f"{base_title} ALT")
    p3 = save_track(delta, title=f"{base_title} Δ(ALT-REF)")
    return p1, p2, p3


class VisualizationGenerator:
    """Professional visualization generator for enhancer detection pipeline."""
    
    def __init__(self, *, output_dir: str = "data/visualizations", dpi: int = 300):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dpi = dpi
    
    def create_enhancer_signature_plot(
        self,
        alphagenome_result: Dict[str, Any],
        enhancer_analysis: Dict[str, Any],
        variant_id: str
    ) -> Optional[str]:
        """Create enhancer signature plot showing key regulatory marks."""
        try:
            # Extract data from AlphaGenome result
            summary = alphagenome_result.get("summary", {})
            
            # Create figure with subplots for different marks
            fig, axes = plt.subplots(2, 2, figsize=(12, 8))
            fig.suptitle(f"Enhancer Signature Analysis: {variant_id}", fontsize=14, fontweight='bold')
            
            # DNase accessibility
            dnase_data = summary.get("dnase", {})
            self._plot_signal_comparison(
                axes[0, 0],
                dnase_data.get("ref_mean", 0),
                dnase_data.get("alt_mean", 0),
                "DNase Accessibility",
                dnase_data.get("max_increase", 0)
            )
            
            # RNA expression  
            rna_data = summary.get("rna_seq", {})
            self._plot_signal_comparison(
                axes[0, 1],
                rna_data.get("ref_mean", 0),
                rna_data.get("alt_mean", 0),
                "RNA Expression",
                rna_data.get("max_increase", 0)
            )
            
            # Histone marks
            histone_data = summary.get("chip_histone", {}).get("marks", {})
            
            # H3K27ac
            h3k27ac = histone_data.get("H3K27ac", {})
            self._plot_signal_comparison(
                axes[1, 0],
                h3k27ac.get("ref_mean", 0),
                h3k27ac.get("alt_mean", 0),
                "H3K27ac (Active Enhancer)",
                h3k27ac.get("max_increase", 0)
            )
            
            # H3K4me1
            h3k4me1 = histone_data.get("H3K4me1", {})
            self._plot_signal_comparison(
                axes[1, 1],
                h3k4me1.get("ref_mean", 0),
                h3k4me1.get("alt_mean", 0),
                "H3K4me1 (Enhancer Mark)",
                h3k4me1.get("max_increase", 0)
            )
            
            # Add enhancer call annotation
            is_enhancer = enhancer_analysis.get("is_enhancer_like", False)
            confidence = enhancer_analysis.get("confidence", "unknown")
            
            fig.text(0.02, 0.02, 
                    f"Enhancer Call: {'YES' if is_enhancer else 'NO'} (Confidence: {confidence.upper()})",
                    fontsize=12, fontweight='bold',
                    color='green' if is_enhancer else 'red')
            
            plt.tight_layout()
            
            # Save plot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"enhancer_signature_{variant_id.replace(':', '_').replace('>', '_')}_{timestamp}.png"
            filepath = self.output_dir / filename
            
            plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
            plt.close(fig)
            
            return str(filepath)
            
        except Exception as e:
            print(f"Failed to create enhancer signature plot: {e}")
            return None
    
    def create_regulatory_landscape_plot(
        self,
        alphagenome_result: Dict[str, Any],
        variant_id: str
    ) -> Optional[str]:
        """Create regulatory landscape overview plot."""
        try:
            raw_data = alphagenome_result.get("raw", {})
            
            if not raw_data or "reference" not in raw_data or "alternate" not in raw_data:
                print("Insufficient raw data for landscape plot")
                return None
            
            ref_outputs = raw_data["reference"]
            alt_outputs = raw_data["alternate"]
            
            # Create comprehensive landscape plot
            fig, axes = plt.subplots(3, 1, figsize=(14, 10))
            fig.suptitle(f"Regulatory Landscape: {variant_id}", fontsize=16, fontweight='bold')
            
            # Plot DNase if available
            if hasattr(ref_outputs, 'dnase') and ref_outputs.dnase is not None:
                self._plot_track_comparison(
                    axes[0],
                    ref_outputs.dnase.values.flatten(),
                    alt_outputs.dnase.values.flatten(),
                    "DNase Accessibility"
                )
            
            # Plot RNA if available  
            if hasattr(ref_outputs, 'rna_seq') and ref_outputs.rna_seq is not None:
                self._plot_track_comparison(
                    axes[1],
                    ref_outputs.rna_seq.values.flatten(),
                    alt_outputs.rna_seq.values.flatten(),
                    "RNA Expression"
                )
            
            # Plot histone marks if available
            if hasattr(ref_outputs, 'chip_histone') and ref_outputs.chip_histone is not None:
                # Use first histone mark for landscape view
                ref_hist = ref_outputs.chip_histone.values
                alt_hist = alt_outputs.chip_histone.values
                
                if ref_hist.size > 0 and alt_hist.size > 0:
                    # Use first mark if multi-dimensional
                    if len(ref_hist.shape) > 1:
                        ref_track = ref_hist[:, 0] if ref_hist.shape[1] > 0 else ref_hist.flatten()
                        alt_track = alt_hist[:, 0] if alt_hist.shape[1] > 0 else alt_hist.flatten()
                    else:
                        ref_track = ref_hist.flatten()
                        alt_track = alt_hist.flatten()
                    
                    self._plot_track_comparison(
                        axes[2],
                        ref_track,
                        alt_track,
                        "Histone Marks"
                    )
            
            plt.tight_layout()
            
            # Save plot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"regulatory_landscape_{variant_id.replace(':', '_').replace('>', '_')}_{timestamp}.png"
            filepath = self.output_dir / filename
            
            plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
            plt.close(fig)
            
            return str(filepath)
            
        except Exception as e:
            print(f"Failed to create regulatory landscape plot: {e}")
            return None
    
    def _plot_signal_comparison(self, ax, ref_mean: float, alt_mean: float, title: str, max_increase: float):
        """Plot reference vs alternate signal comparison."""
        x = ['Reference', 'Alternate']
        y = [ref_mean, alt_mean]
        
        colors = ['blue', 'red' if alt_mean > ref_mean else 'orange']
        bars = ax.bar(x, y, color=colors, alpha=0.7)
        
        ax.set_title(title, fontweight='bold')
        ax.set_ylabel('Signal Intensity')
        
        # Add value labels on bars
        for bar, value in zip(bars, y):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(y) * 0.01,
                   f'{value:.4f}', ha='center', va='bottom', fontsize=10)
        
        # Add delta annotation
        delta = alt_mean - ref_mean
        ax.text(0.5, max(y) * 0.8, f'Δ = {delta:.4f}\nMax Δ = {max_increase:.4f}',
               ha='center', va='center', fontsize=10,
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    def _plot_track_comparison(self, ax, ref_track: np.ndarray, alt_track: np.ndarray, title: str):
        """Plot reference vs alternate tracks."""
        positions = np.arange(len(ref_track))
        
        ax.plot(positions, ref_track, label='Reference', color='blue', alpha=0.7)
        ax.plot(positions, alt_track, label='Alternate', color='red', alpha=0.7)
        
        # Highlight differences
        delta = alt_track - ref_track
        ax.fill_between(positions, ref_track, alt_track, 
                       where=(delta > 0), alpha=0.3, color='red', label='Increase')
        ax.fill_between(positions, ref_track, alt_track,
                       where=(delta < 0), alpha=0.3, color='blue', label='Decrease')
        
        ax.set_title(title, fontweight='bold')
        ax.set_xlabel('Position (bp)')
        ax.set_ylabel('Signal Intensity')
        ax.legend()
        ax.grid(True, alpha=0.3)