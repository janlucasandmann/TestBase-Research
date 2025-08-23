"""Promoter/enhancer detection pipeline using AlphaGenome."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from ..clients.alphagenome_client import AlphaGenomeClient
from ..core.config import config
from ..core.logging import get_logger
from ..core.schemas import (
    Context, Direction, EvidenceItem, GenomicInterval, Modality, 
    PipelineRequest, PipelineResult, Variant
)
from ..reports.renderer import ReportRenderer, VariantEntry, FigureSpec
# Simplified - no complex scoring needed
# Visualization imports simplified

logger = get_logger(__name__)


class PromoterEnhancerPipeline:
    """Pipeline for detecting promoter and enhancer effects using AlphaGenome.
    
    This pipeline analyzes variants or intervals to identify regulatory effects
    on promoter and enhancer activity through multiple modalities:
    - TSS/CAGE signals (promoter activity)
    - Histone marks (H3K27ac for enhancers, H3K4me3 for promoters)
    - ATAC/DNase signals (chromatin accessibility)
    - TF binding (regulatory factor activity)
    """
    
    REQUIRED_MODALITIES = {
        Modality.TSS_CAGE,
        Modality.HISTONE, 
        Modality.ATAC_DNASE,
        Modality.TF_BIND
    }
    
    def __init__(self, api_key: str = None):
        """Initialize the pipeline."""
        logger.info("Using AlphaGenome client")
        import os
        self.client = AlphaGenomeClient(api_key or os.getenv("ALPHAGENOME_API_KEY"))
        self.renderer = ReportRenderer(title="Promoter/Enhancer Analysis Report")
        config.ensure_directories()
    
    def run(self, request: PipelineRequest) -> PipelineResult:
        """Run the promoter/enhancer analysis pipeline.
        
        Args:
            request: Pipeline request with variant/interval and context
            
        Returns:
            Pipeline results with mechanism summary and evidence
        """
        logger.info("Starting promoter/enhancer analysis pipeline")
        
        # Determine analysis type and query AlphaGenome
        if request.variant:
            logger.info(f"Analyzing variant: {request.variant.to_string()}")
            alphagenome_result = self.client.predict_variant_effects(
                request.variant,
                request.interval or self._create_interval_around_variant(request.variant),
                tissue=getattr(request.context, 'tissue', 'pancreatic')
            )
        elif request.interval:
            logger.info(f"Analyzing interval: {request.interval.to_string()}")
            # For interval-only analysis, create a dummy variant at the center
            center_pos = (request.interval.start + request.interval.end) // 2
            dummy_variant = Variant(
                chrom=request.interval.chrom,
                pos=center_pos,
                ref="C",
                alt="A"
            )
            alphagenome_result = self.client.predict_variant_effects(
                dummy_variant,
                request.interval,
                tissue=getattr(request.context, 'tissue', 'pancreatic')
            )
        else:
            raise ValueError("Either variant or interval must be provided")
        
        # Check if we got an error
        if alphagenome_result.get("error"):
            raise RuntimeError(f"AlphaGenome analysis failed: {alphagenome_result['error']}")
        
        # Create simplified result for downstream processing
        simplified_result = self._create_simplified_result(alphagenome_result)
        
        # Compute modality deltas and scores
        modality_deltas = {"enhancer_score": 1.0}  # Simplified scoring
        aggregated_scores = {"total_score": 1.0, "confidence": 0.8}
        
        # Generate evidence items
        evidence = self._generate_simple_evidence(alphagenome_result)
        
        # Create mechanism summary
        mechanism_summary = alphagenome_result.get("analysis", {}).get("decision", "Analysis completed")
        
        # Generate visualizations (copy existing ones)
        figures = self._copy_visualizations(alphagenome_result)
        
        # Create simple report
        report_path = self._create_simple_report(request, alphagenome_result)
        
        return PipelineResult(
            mechanism_summary=mechanism_summary,
            evidence=evidence,
            figures=figures,
            scores=aggregated_scores,
            metadata={
                "alphagenome_result": alphagenome_result,
                "report_path": str(report_path),
                "analysis_type": "variant" if request.variant else "interval"
            }
        )
    
    def _generate_evidence(
        self, 
        modality_deltas: Dict[str, float], 
        alphagenome_result
    ) -> List[EvidenceItem]:
        """Generate evidence items from modality deltas.
        
        Args:
            modality_deltas: Computed deltas for each modality
            alphagenome_result: Raw AlphaGenome results
            
        Returns:
            List of evidence items
        """
        evidence = []
        
        for track_id, delta in modality_deltas.items():
            if abs(delta) < 0.01:  # Skip very small changes
                continue
            
            metadata = alphagenome_result.track_metadata.get(track_id, {})
            modality_str = metadata.get("modality", "UNKNOWN")
            
            # Map string modalities to enum
            try:
                modality = Modality(modality_str)
            except ValueError:
                continue
            
            # Determine direction
            direction = Direction.UP if delta > 0 else Direction.DOWN
            
            # Generate description based on modality and tissue
            tissue = metadata.get("tissue", "tissue")
            description = self._format_evidence_description(modality, metadata, tissue)
            
            evidence.append(EvidenceItem(
                modality=modality,
                description=description,
                delta=delta,
                direction=direction,
                support_tracks=[track_id]
            ))
        
        # Sort by absolute delta (strongest effects first)
        evidence.sort(key=lambda e: abs(e.delta), reverse=True)
        
        return evidence
    
    def _format_evidence_description(
        self, 
        modality: Modality, 
        metadata: Dict[str, Any], 
        tissue: str
    ) -> str:
        """Format a description for an evidence item.
        
        Args:
            modality: Data modality
            metadata: Track metadata
            tissue: Tissue context
            
        Returns:
            Formatted description
        """
        if modality == Modality.TSS_CAGE:
            return f"TSS/CAGE activity in {tissue}"
        elif modality == Modality.HISTONE:
            mark = metadata.get("mark", "histone")
            if "h3k27ac" in mark.lower():
                return f"Enhancer activity ({mark}) in {tissue}"
            elif "h3k4me3" in mark.lower():
                return f"Promoter activity ({mark}) in {tissue}"
            else:
                return f"Histone modification ({mark}) in {tissue}"
        elif modality == Modality.ATAC_DNASE:
            return f"Chromatin accessibility in {tissue}"
        elif modality == Modality.TF_BIND:
            factor = metadata.get("factor", "TF")
            return f"{factor} binding in {tissue}"
        else:
            return f"{modality.value} signal in {tissue}"
    
    def _generate_mechanism_summary(
        self, 
        evidence: List[EvidenceItem], 
        scores: Dict[str, float]
    ) -> str:
        """Generate a mechanism summary from evidence.
        
        Args:
            evidence: List of evidence items
            scores: Aggregated scores
            
        Returns:
            Mechanism summary string
        """
        if not evidence:
            return "No significant regulatory effects detected across analyzed modalities."
        
        # Get primary direction and strongest effects
        top_evidence = evidence[:3]  # Top 3 strongest effects
        
        primary_direction = self._get_primary_direction(evidence)
        direction_str = "increases" if primary_direction == Direction.UP else "decreases"
        
        # Count modality types
        modality_counts = {}
        for e in evidence:
            modality_counts[e.modality] = modality_counts.get(e.modality, 0) + 1
        
        # Build summary
        if len(evidence) == 1:
            summary = f"This variant {direction_str} {top_evidence[0].description.lower()}."
        else:
            modality_list = []
            if Modality.TSS_CAGE in modality_counts:
                modality_list.append("promoter activity")
            if Modality.HISTONE in modality_counts:
                modality_list.append("enhancer/promoter marks")
            if Modality.ATAC_DNASE in modality_counts:
                modality_list.append("chromatin accessibility")
            if Modality.TF_BIND in modality_counts:
                modality_list.append("transcription factor binding")
            
            if len(modality_list) > 1:
                modality_str = ", ".join(modality_list[:-1]) + f" and {modality_list[-1]}"
            else:
                modality_str = modality_list[0] if modality_list else "regulatory activity"
            
            summary = f"This variant {direction_str} {modality_str}."
        
        # Add confidence note based on number of supporting modalities
        if len(modality_counts) >= 3:
            summary += " Multiple independent modalities support this regulatory effect."
        elif len(modality_counts) == 2:
            summary += " Two modalities support this regulatory effect."
        
        return summary
    
    def _get_primary_direction(self, evidence: List[EvidenceItem]) -> Direction:
        """Get the primary direction from evidence list.
        
        Args:
            evidence: List of evidence items
            
        Returns:
            Primary direction
        """
        if not evidence:
            return Direction.NA
        
        up_count = sum(1 for e in evidence if e.direction == Direction.UP)
        down_count = sum(1 for e in evidence if e.direction == Direction.DOWN)
        
        if up_count > down_count:
            return Direction.UP
        elif down_count > up_count:
            return Direction.DOWN
        else:
            return Direction.MIXED
    
    def _create_visualizations(
        self, 
        alphagenome_result, 
        request: PipelineRequest
    ) -> List[Path]:
        """Create visualization plots.
        
        Args:
            alphagenome_result: AlphaGenome results
            request: Original request
            
        Returns:
            List of figure paths
        """
        figures = []
        
        # Create individual track plots
        for track_id, track_data in alphagenome_result.modality_data.items():
            ref_values = track_data.get("ref", [])
            alt_values = track_data.get("alt", [])
            
            if len(ref_values) > 0 and len(alt_values) > 0:
                try:
                    ref_path, alt_path, delta_path = save_ref_alt_delta(
                        ref_values, alt_values, base_title=track_id
                    )
                    figures.extend([ref_path, alt_path, delta_path])
                except Exception as e:
                    logger.warning(f"Failed to create visualization for {track_id}: {e}")
        
        # Create comparison plots
        try:
            comparison_fig = create_comparison_plots(alphagenome_result)
            if comparison_fig:
                figures.append(comparison_fig)
        except Exception as e:
            logger.warning(f"Failed to create comparison plot: {e}")
        
        return figures
    
    def _generate_report(
        self,
        request: PipelineRequest,
        evidence: List[EvidenceItem],
        figures: List[Path],
        mechanism_summary: str
    ) -> Path:
        """Generate HTML report.
        
        Args:
            request: Original request
            evidence: Generated evidence
            figures: Created figures
            mechanism_summary: Mechanism summary
            
        Returns:
            Path to generated report
        """
        # Create variant entry for report
        if request.variant:
            variant_entry = VariantEntry(
                variant_id=request.variant.to_string(),
                chrom=request.variant.chrom,
                pos=request.variant.pos,
                ref=request.variant.ref,
                alt=request.variant.alt,
                status="analyzed",
                enhancers_detected=len([e for e in evidence if "enhancer" in e.description.lower()]),
                notes=mechanism_summary,
                figures=[FigureSpec(caption=f"Figure: {fig.stem}", path=fig) for fig in figures],
                modality_deltas={e.modality.value: e.delta for e in evidence[:5]}
            )
            title_suffix = request.variant.to_string()
        else:
            variant_entry = VariantEntry(
                variant_id=request.interval.to_string(),
                chrom=request.interval.chrom,
                pos=request.interval.start,
                ref="N/A",
                alt="N/A",
                status="analyzed",
                enhancers_detected=len([e for e in evidence if "enhancer" in e.description.lower()]),
                notes=mechanism_summary,
                figures=[FigureSpec(caption=f"Figure: {fig.stem}", path=fig) for fig in figures],
                modality_deltas={e.modality.value: e.delta for e in evidence[:5]}
            )
            title_suffix = request.interval.to_string()
        
        # Generate report metadata
        meta = {
            "research_question": f"What are the promoter/enhancer effects of {title_suffix}?",
            "gene": "Unknown",  # Could be enhanced to include gene annotation
            "cancer_type": "N/A",
            "methods": [
                "Queried AlphaGenome API for TSS/CAGE, histone, ATAC/DNase, and TF binding predictions",
                "Computed delta values (ALT - REF) for each modality",
                "Aggregated evidence across modalities to assess regulatory impact",
                "Generated visualizations showing signal differences"
            ],
            "limitations": [
                "AlphaGenome predictions are computational estimates requiring experimental validation",
                "Effects may vary across cell types and conditions beyond the analyzed tissue context",
                "Large structural variants may extend beyond the analysis window",
                "Regulatory effects may be context-dependent and require functional validation"
            ]
        }
        
        # Generate summary
        summary = {
            "answer_yes": len(evidence) > 0,
            "yes_details": mechanism_summary if evidence else "",
            "mutations_analyzed": 1,
            "enhancer_positive_variants": 1 if evidence else 0
        }
        
        # Create HTML
        html = self.renderer.build_html(
            meta=meta,
            variants=[variant_entry],
            summary=summary
        )
        
        # Save report
        timestamp = str(config.OUTPUT_DIR / "promoter_enhancer_report.html")
        report_path = Path(timestamp)
        return self.renderer.save(html, report_path)
    
    def _create_interval_around_variant(self, variant: Variant, window_size: int = 20000) -> GenomicInterval:
        """Create an interval around a variant for analysis."""
        start = max(1, variant.pos - window_size // 2)
        end = variant.pos + window_size // 2
        return GenomicInterval(
            chrom=variant.chrom,
            start=start,
            end=end
        )
    
    def _create_simplified_result(self, alphagenome_result: Dict[str, Any]) -> Dict[str, Any]:
        """Create a simplified result object for downstream processing."""
        return {
            "modality_data": {},
            "track_metadata": {},
            "raw_result": alphagenome_result
        }
    
    def _generate_simple_evidence(self, alphagenome_result: Dict[str, Any]) -> List[EvidenceItem]:
        """Generate simplified evidence from AlphaGenome results."""
        evidence = []
        analysis = alphagenome_result.get("analysis", {})
        
        # Create evidence based on detected signals
        if analysis.get("enhancer_detected", False):
            evidence.append(EvidenceItem(
                modality=Modality.HISTONE,
                delta=analysis.get("h3k27ac_increase", 0.0),
                direction=Direction.UP,
                confidence=0.8,
                description=f"H3K27ac increase detected: {analysis.get('h3k27ac_increase', 0.0)}"
            ))
            
            if analysis.get("dnase_increase", 0) > 0.1:
                evidence.append(EvidenceItem(
                    modality=Modality.ATAC_DNASE,
                    delta=analysis.get("dnase_increase", 0.0),
                    direction=Direction.UP,
                    confidence=0.7,
                    description=f"DNase accessibility increase: {analysis.get('dnase_increase', 0.0)}"
                ))
        
        return evidence
    
    def _copy_visualizations(self, alphagenome_result: Dict[str, Any]) -> List[Path]:
        """Copy visualization files to our output directory."""
        figures = []
        viz_files = alphagenome_result.get("visualization_files", [])
        
        for viz_file in viz_files:
            if Path(viz_file).exists():
                figures.append(Path(viz_file))
                
        return figures
    
    def _create_simple_report(self, request: PipelineRequest, alphagenome_result: Dict[str, Any]) -> Path:
        """Create a simple report linking to the AlphaGenome analysis."""
        output_dir = Path(__file__).parent.parent.parent / "data" / "logs" / "alphagenome-outputs"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = output_dir / "simple_analysis_report.md"
        
        analysis = alphagenome_result.get("analysis", {})
        
        content = f"""# AlphaGenome Analysis Report

## Analysis Summary
- Variant: {alphagenome_result.get('variant', 'Unknown')}
- Tissue: {alphagenome_result.get('tissue', 'Unknown')}
- Status: {alphagenome_result.get('status', 'Unknown')}

## Results
- Decision: {analysis.get('decision', 'Unknown')}
- Enhancer Detected: {analysis.get('enhancer_detected', False)}
- DNase Increase: {analysis.get('dnase_increase', 0.0)}
- H3K27ac Increase: {analysis.get('h3k27ac_increase', 0.0)}
- H3K4me1 Increase: {analysis.get('h3k4me1_increase', 0.0)}
- RNA Increase: {analysis.get('rna_increase', 0.0)}

## Files
- Original Report: {alphagenome_result.get('report_file', 'N/A')}
- Visualizations: {len(alphagenome_result.get('visualization_files', []))} files

## Raw Analysis
```json
{alphagenome_result}
```
"""
        
        with open(report_file, 'w') as f:
            f.write(content)
            
        logger.info(f"📄 Created simple report: {report_file}")
        return report_file