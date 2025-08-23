"""
Professional enhancer detection visualization with base-pair level expression graphs.

Creates genome browser-style visualizations showing REF vs ALT signals across
the genomic window with quantitative analysis and detection verdict.
"""

from __future__ import annotations
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import seaborn as sns

# Set up professional plotting style
plt.style.use('default')
sns.set_palette("husl")


class EnhancerBrowserVisualizer:
    """
    Professional genome browser-style visualization for enhancer detection.
    
    Creates publication-quality figures showing:
    - Base-pair level signal tracks (REF vs ALT)
    - Quantitative delta analysis
    - Mutation position markers
    - Professional detection verdict
    """
    
    def __init__(self, output_dir: str = "data/visualizations", dpi: int = 300):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dpi = dpi
        
        # Professional color scheme
        self.colors = {
            'ref': '#2E86AB',        # Professional blue
            'alt': '#A23B72',        # Professional purple/red
            'delta_positive': '#F18F01',  # Orange for increases
            'delta_negative': '#C73E1D',  # Red for decreases
            'enhancer': '#4CAF50',   # Green for enhancer marks
            'promoter': '#FF9800',   # Orange for promoter marks
            'accessibility': '#2196F3',  # Blue for accessibility
            'mutation': '#E91E63',   # Pink for mutation marker
            'background': '#F8F9FA', # Light gray background
            'grid': '#E0E0E0'        # Grid color
        }
    
    def create_unified_enhancer_visualization(
        self,
        alphagenome_result: Dict[str, Any],
        detection_result: Dict[str, Any],
        variant_id: str,
        tissue_context: Optional[str] = None
    ) -> Optional[str]:
        """
        Create unified enhancer detection visualization with base-pair level graphs.
        
        Args:
            alphagenome_result: Raw AlphaGenome API result
            detection_result: Professional detection result
            variant_id: Variant identifier (chr:pos:ref>alt)
            tissue_context: Tissue context for display
            
        Returns:
            Path to generated visualization file
        """
        try:
            # Extract raw data for base-pair level plotting
            raw_data = alphagenome_result.get("raw", {})
            if not raw_data or "reference" not in raw_data:
                print("⚠️ Insufficient raw data for detailed visualization")
                return None
            
            ref_outputs = raw_data["reference"]
            alt_outputs = raw_data["alternate"]
            
            # Create the unified figure
            fig = plt.figure(figsize=(16, 12))
            fig.patch.set_facecolor(self.colors['background'])
            
            # Parse variant information
            variant_parts = variant_id.split(":")
            if len(variant_parts) >= 4:
                chrom, pos, ref_alt = variant_parts[0], int(variant_parts[1]), variant_parts[2] + ">" + variant_parts[3]
            else:
                chrom, pos, ref_alt = "Unknown", 0, variant_id
            
            # Create title with mutation information
            tissue_str = f" | {tissue_context}" if tissue_context else ""
            fig.suptitle(f"Enhancer Detection Analysis: {variant_id}{tissue_str}", 
                        fontsize=16, fontweight='bold', y=0.95)
            
            # Create grid layout for tracks
            n_tracks = 5  # DNase, H3K27ac, H3K4me1, H3K4me3, RNA
            gs = fig.add_gridspec(n_tracks + 2, 3, 
                                height_ratios=[0.4] + [1]*n_tracks + [0.5],
                                width_ratios=[2, 2, 1],
                                hspace=0.6, wspace=0.3)  # Increased vertical spacing
            
            # 1. Genomic coordinate track (top)
            coord_ax = fig.add_subplot(gs[0, :2])
            self._plot_genomic_coordinates(coord_ax, pos, alphagenome_result.get("interval_bp", 131072))
            
            # 2. Signal tracks with base-pair level graphs
            track_names = ["DNase", "H3K27ac", "H3K4me1", "H3K4me3", "RNA"]
            track_data = self._extract_track_data(ref_outputs, alt_outputs)
            
            for i, track_name in enumerate(track_names):
                # Left panel: REF signal
                ref_ax = fig.add_subplot(gs[i+1, 0])
                # Right panel: ALT signal  
                alt_ax = fig.add_subplot(gs[i+1, 1])
                
                if track_name.lower() in track_data:
                    self._plot_signal_track_pair(
                        ref_ax, alt_ax, track_data[track_name.lower()], 
                        track_name, pos, alphagenome_result.get("interval_bp", 131072)
                    )
                else:
                    # No data available
                    self._plot_no_data_track(ref_ax, alt_ax, track_name)
            
            # 3. Detection verdict panel (bottom right)
            verdict_ax = fig.add_subplot(gs[1:, 2])
            self._plot_detection_verdict(verdict_ax, detection_result, alphagenome_result.get("summary", {}))
            
            # Save the visualization
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_variant = variant_id.replace(":", "_").replace(">", "_")
            filename = f"unified_enhancer_analysis_{safe_variant}_{timestamp}.png"
            filepath = self.output_dir / filename
            
            plt.tight_layout()
            plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight', 
                       facecolor=self.colors['background'])
            plt.close(fig)
            
            return str(filepath)
            
        except Exception as e:
            print(f"❌ Failed to create unified enhancer visualization: {e}")
            # Don't print full traceback in production, just log the error
            return None
    
    def _extract_track_data(self, ref_outputs, alt_outputs) -> Dict[str, Dict[str, np.ndarray]]:
        """Extract base-pair level data from AlphaGenome outputs."""
        track_data = {}
        
        # DNase accessibility
        if hasattr(ref_outputs, 'dnase') and ref_outputs.dnase is not None:
            ref_values = ref_outputs.dnase.values.flatten()
            alt_values = alt_outputs.dnase.values.flatten()
            track_data['dnase'] = {'ref': ref_values, 'alt': alt_values}
        
        # RNA expression
        if hasattr(ref_outputs, 'rna_seq') and ref_outputs.rna_seq is not None:
            ref_values = ref_outputs.rna_seq.values.flatten()
            alt_values = alt_outputs.rna_seq.values.flatten()
            track_data['rna'] = {'ref': ref_values, 'alt': alt_values}
        
        # Histone modifications
        if hasattr(ref_outputs, 'chip_histone') and ref_outputs.chip_histone is not None:
            ref_hist = ref_outputs.chip_histone.values
            alt_hist = alt_outputs.chip_histone.values
            
            if ref_hist.size > 0 and alt_hist.size > 0:
                # Get metadata to identify marks
                metadata = getattr(ref_outputs.chip_histone, 'metadata', None)
                mark_names = []
                if metadata is not None:
                    try:
                        # Handle different metadata formats
                        if hasattr(metadata, 'get') and not hasattr(metadata, 'empty'):
                            # Dictionary-like metadata
                            mark_names = list(metadata.get("name", []))
                        elif hasattr(metadata, 'empty'):
                            # DataFrame metadata - check if not empty
                            if not metadata.empty and "name" in metadata:
                                mark_names = list(metadata["name"].values)
                        else:
                            # Try to extract as list/array
                            try:
                                mark_names = list(metadata) if hasattr(metadata, '__iter__') else []
                            except:
                                mark_names = []
                    except Exception as e:
                        print(f"Warning: Could not extract histone mark names: {e}")
                        mark_names = []
                
                # Map common histone marks
                if mark_names:
                    for i, mark_name in enumerate(mark_names):
                        if i < (ref_hist.shape[1] if len(ref_hist.shape) > 1 else 1):
                            if len(ref_hist.shape) > 1:
                                ref_track = ref_hist[:, i]
                                alt_track = alt_hist[:, i]
                            else:
                                ref_track = ref_hist
                                alt_track = alt_hist
                            
                            # Map to standard names
                            track_key = None
                            mark_str = str(mark_name).lower()
                            if 'h3k27ac' in mark_str:
                                track_key = 'h3k27ac'
                            elif 'h3k4me1' in mark_str:
                                track_key = 'h3k4me1'
                            elif 'h3k4me3' in mark_str:
                                track_key = 'h3k4me3'
                            
                            if track_key:
                                track_data[track_key] = {'ref': ref_track, 'alt': alt_track}
                else:
                    # Fallback: assume first few columns are common marks
                    print("Warning: No histone mark names found, using positional mapping")
                    n_marks = min(3, ref_hist.shape[1] if len(ref_hist.shape) > 1 else 1)
                    mark_keys = ['h3k27ac', 'h3k4me1', 'h3k4me3'][:n_marks]
                    
                    for i, track_key in enumerate(mark_keys):
                        if len(ref_hist.shape) > 1 and i < ref_hist.shape[1]:
                            ref_track = ref_hist[:, i]
                            alt_track = alt_hist[:, i]
                            track_data[track_key] = {'ref': ref_track, 'alt': alt_track}
        
        return track_data
    
    def _plot_genomic_coordinates(self, ax, variant_pos: int, window_size: int):
        """Plot genomic coordinate ruler with mutation marker."""
        start_pos = variant_pos - window_size // 2
        end_pos = variant_pos + window_size // 2
        
        # Create coordinate axis - use same coordinate system as tracks (0 to window_size)
        ax.set_xlim(0, window_size)
        ax.set_ylim(-0.5, 0.5)
        
        # Draw ruler
        ax.axhline(0, color='black', linewidth=2)
        
        # Add tick marks - show actual genomic positions (all positive)
        n_ticks = 6  # Fewer ticks to avoid crowding
        for i in range(n_ticks + 1):
            x_pos = i * window_size / n_ticks  # Position in track coordinates (0 to window_size)
            genomic_pos = start_pos + x_pos     # Actual genomic position
            ax.axvline(x_pos, ymin=0.3, ymax=0.7, color='black', linewidth=1)
            # Show actual genomic positions (positive values only)
            ax.text(x_pos, -0.35, f"{abs(genomic_pos)/1000:.0f}k", 
                   ha='center', va='top', fontsize=9, rotation=45)  # Rotate to prevent overlap
        
        # Mark mutation position - same coordinate system as tracks
        mut_x = window_size // 2  # Center of window (matches track coordinates)
        ax.axvline(mut_x, color=self.colors['mutation'], linewidth=4, alpha=0.9)
        ax.scatter(mut_x, 0, color=self.colors['mutation'], s=120, zorder=10, marker='v')
        
        # Place mutation label above the ruler to avoid overlap
        ax.text(mut_x, 0.35, "MUTATION", ha='center', va='center', 
               fontweight='bold', color=self.colors['mutation'], fontsize=10,
               bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
        
        ax.set_title("Genomic Position", fontweight='bold', pad=20)  # Increased padding
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
    
    def _plot_signal_track_pair(self, ref_ax, alt_ax, track_data: Dict[str, np.ndarray], 
                               track_name: str, variant_pos: int, window_size: int):
        """Plot paired REF/ALT signal tracks with base-pair resolution."""
        ref_values = track_data['ref']
        alt_values = track_data['alt']
        
        # Create position array
        positions = np.arange(len(ref_values))
        
        # Determine track color
        track_color = self.colors['enhancer']  # Default
        if track_name in ['H3K27ac', 'H3K4me1']:
            track_color = self.colors['enhancer']
        elif track_name == 'H3K4me3':
            track_color = self.colors['promoter']
        elif track_name == 'DNase':
            track_color = self.colors['accessibility']
        
        # Plot REF signal
        ref_ax.fill_between(positions, ref_values, alpha=0.6, color=self.colors['ref'], label='Reference')
        ref_ax.plot(positions, ref_values, color=self.colors['ref'], linewidth=1.5)
        ref_ax.set_title(f"{track_name} - Reference", fontsize=10, fontweight='bold', pad=15)
        ref_ax.grid(True, alpha=0.3, color=self.colors['grid'])
        
        # Plot ALT signal
        alt_ax.fill_between(positions, alt_values, alpha=0.6, color=self.colors['alt'], label='Alternate')
        alt_ax.plot(positions, alt_values, color=self.colors['alt'], linewidth=1.5)
        alt_ax.set_title(f"{track_name} - Alternate", fontsize=10, fontweight='bold', pad=15)
        alt_ax.grid(True, alpha=0.3, color=self.colors['grid'])
        
        # Mark mutation position on both plots - same position as coordinate ruler
        mut_x = len(positions) // 2  # Center position matches coordinate ruler
        for ax in [ref_ax, alt_ax]:
            ax.axvline(mut_x, color=self.colors['mutation'], linestyle='--', alpha=0.9, linewidth=2)
        
        # Add quantitative summary
        ref_mean = np.mean(ref_values)
        alt_mean = np.mean(alt_values)
        delta = alt_mean - ref_mean
        
        # Add delta text - move to avoid overlap
        delta_color = self.colors['delta_positive'] if delta > 0 else self.colors['delta_negative']
        alt_ax.text(0.98, 0.85, f"Δ = {delta:+.4f}", transform=alt_ax.transAxes,
                   ha='right', va='top', fontweight='bold', fontsize=9,
                   bbox=dict(boxstyle='round,pad=0.3', facecolor=delta_color, alpha=0.9),
                   color='white')
        
        # Set axis properties
        for ax in [ref_ax, alt_ax]:
            ax.set_xlim(0, len(positions))
            ax.tick_params(axis='both', labelsize=8)
            if np.max([np.max(ref_values), np.max(alt_values)]) > 0:
                ax.set_ylim(0, np.max([np.max(ref_values), np.max(alt_values)]) * 1.1)
    
    def _plot_no_data_track(self, ref_ax, alt_ax, track_name: str):
        """Plot placeholder for tracks with no data."""
        for ax, label in [(ref_ax, "Reference"), (alt_ax, "Alternate")]:
            ax.text(0.5, 0.5, f"No {track_name} data\navailable", 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=9, style='italic', color='gray')
            ax.set_title(f"{track_name} - {label}", fontsize=10, fontweight='bold', pad=15)
            ax.set_xticks([])
            ax.set_yticks([])
    
    def _plot_detection_verdict(self, ax, detection_result: Dict[str, Any], summary: Dict[str, Any]):
        """Plot professional detection verdict panel."""
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xticks([])
        ax.set_yticks([])
        
        # Get professional detection data
        prof_detection = detection_result.get("professional_detection", {})
        is_enhancer = prof_detection.get("is_enhancer_like", False)
        confidence = prof_detection.get("confidence", "unknown")
        positive_marks = prof_detection.get("positive_marks", [])
        total_score = prof_detection.get("total_evidence_score", 0)
        interpretation = prof_detection.get("interpretation", "No interpretation available")
        
        # Title
        ax.text(0.5, 0.95, "DETECTION VERDICT", ha='center', va='top', 
               fontsize=14, fontweight='bold', transform=ax.transAxes)
        
        # Main verdict
        verdict_color = self.colors['enhancer'] if is_enhancer else self.colors['delta_negative']
        verdict_text = "✅ ENHANCER DETECTED" if is_enhancer else "❌ NO ENHANCER"
        
        ax.text(0.5, 0.85, verdict_text, ha='center', va='top',
               fontsize=12, fontweight='bold', color=verdict_color,
               transform=ax.transAxes)
        
        # Confidence
        ax.text(0.5, 0.75, f"Confidence: {confidence.upper()}", ha='center', va='top',
               fontsize=11, fontweight='bold', transform=ax.transAxes)
        
        # Evidence summary
        ax.text(0.02, 0.65, "Evidence:", ha='left', va='top',
               fontsize=10, fontweight='bold', transform=ax.transAxes)
        
        # Positive marks
        y_pos = 0.58
        for mark in positive_marks[:5]:  # Show first 5 marks
            mark_display = mark.replace("_", " ").title()
            ax.text(0.05, y_pos, f"• {mark_display}", ha='left', va='top',
                   fontsize=9, color=self.colors['enhancer'], transform=ax.transAxes)
            y_pos -= 0.06
        
        # Evidence score
        ax.text(0.02, 0.25, f"Evidence Score: {total_score:.1f}/10", 
               ha='left', va='top', fontsize=10, fontweight='bold',
               transform=ax.transAxes)
        
        # Algorithm used
        algorithm = prof_detection.get("algorithm_used", "unknown")
        ax.text(0.02, 0.18, f"Algorithm: {algorithm.title()}", 
               ha='left', va='top', fontsize=9, transform=ax.transAxes)
        
        # Quantitative summary
        ax.text(0.02, 0.08, "Quantitative Summary:", 
               ha='left', va='top', fontsize=9, fontweight='bold',
               transform=ax.transAxes)
        
        # Extract key metrics
        dnase_increase = summary.get("dnase", {}).get("max_increase", 0)
        h3k27ac_increase = summary.get("chip_histone", {}).get("marks", {}).get("H3K27ac", {}).get("max_increase", 0)
        rna_increase = summary.get("rna_seq", {}).get("max_increase", 0)
        
        metrics_y = 0.02
        metrics = [
            f"DNase Δ: {dnase_increase:+.4f}",
            f"H3K27ac Δ: {h3k27ac_increase:+.4f}", 
            f"RNA Δ: {rna_increase:+.6f}"
        ]
        
        for metric in metrics:
            ax.text(0.05, metrics_y, metric, ha='left', va='bottom',
                   fontsize=8, transform=ax.transAxes)
            metrics_y += 0.03
        
        # Add border
        rect = patches.Rectangle((0.01, 0.01), 0.98, 0.98, 
                               linewidth=2, edgecolor='black', 
                               facecolor='none', transform=ax.transAxes)
        ax.add_patch(rect)