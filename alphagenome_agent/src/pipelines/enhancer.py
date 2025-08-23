"""Professional Enhancer Detection Pipeline for Cancer Research.

This pipeline uses real mutation data from cBioPortal and AlphaGenome analysis 
to detect enhancer-like regulatory effects of cancer mutations.
"""

from __future__ import annotations
import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from datetime import datetime

from .base import BasePipeline
from ..clients.alphagenome_client import VariantSpec
from ..reports.html_chartjs import ChartJSReportGenerator
from ..scoring.detectors import DetectorFactory, DetectionAlgorithm, ConfidenceLevel
from ..scoring.enhanced_detectors import (
    ScientificEnhancerDetector, 
    GenomicContext, 
    RegionType,
    GenomicAnnotator
)


class EnhancerDetectionPipeline(BasePipeline):
    """
    Professional enhancer detection pipeline for cancer mutations.
    
    Uses real data from cBioPortal + AlphaGenome to identify mutations
    that create enhancer-like regulatory signatures.
    """
    
    # Scientific thresholds based on literature (can be tuned)
    DEFAULT_ENHANCER_CRITERIA = {
        "dnase_min_increase": 0.01,     # Minimum DNase accessibility increase
        "h3k27ac_min_increase": 0.1,    # Minimum H3K27ac (active enhancer mark)
        "h3k4me1_min_increase": 0.05,   # Minimum H3K4me1 (enhancer mark)
        "rna_min_increase": 0.001,      # Minimum RNA expression increase
        "min_marks_required": 2         # Minimum number of marks to call enhancer
    }
    
    def __init__(
        self,
        *,
        alphagenome_api_key: str,
        output_dir: str = "data/enhancer_outputs",
        enhancer_criteria: Optional[Dict[str, float]] = None,
        detection_algorithm: DetectionAlgorithm = DetectionAlgorithm.BALANCED,
        use_scientific_detector: bool = True,  # Use new scientific detector by default
        **kwargs
    ):
        super().__init__(alphagenome_api_key=alphagenome_api_key, **kwargs)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.enhancer_criteria = enhancer_criteria or self.DEFAULT_ENHANCER_CRITERIA
        self.detection_algorithm = detection_algorithm
        self.use_scientific_detector = use_scientific_detector
        
        # Initialize detection modules
        if use_scientific_detector:
            # Use new scientifically rigorous detector
            self.scientific_detector = ScientificEnhancerDetector(strict_mode=True)
            self.genomic_annotator = GenomicAnnotator()
        
        # Keep legacy detector for comparison
        self.enhancer_detector = DetectorFactory.create_enhancer_detector(detection_algorithm)
        
        # Initialize HTML report generator with Chart.js
        self.report_generator = ChartJSReportGenerator(output_dir=str(self.output_dir))
    
    def analyze_variant(self, mutation: Dict[str, Any], tissue_ontology_id: str) -> Dict[str, Any]:
        """
        Analyze a single mutation for enhancer-like effects using AlphaGenome.
        
        Args:
            mutation: Formatted mutation dict from cBioPortal
            tissue_ontology_id: UBERON tissue ontology ID
            
        Returns:
            Analysis result dict with enhancer predictions
        """
        try:
            # Convert mutation to VariantSpec
            variant_spec = self.mutation_to_variant_spec(mutation)
            
            print(f"   Analyzing: {variant_spec.chrom}:{variant_spec.pos}:{variant_spec.ref}>{variant_spec.alt}")
            
            # Call AlphaGenome with appropriate window size for enhancers
            # Using 131072bp (128kb) window to capture long-range regulatory effects
            ag_result = self.alphagenome_client.predict_variant_effects(
                variant=variant_spec,
                interval_bp=131072,  # 128kb window
                tissue=self._map_tissue_to_alphagenome(tissue_ontology_id)
            )
            
            if self.use_scientific_detector:
                # Create genomic context
                genomic_context = GenomicContext(
                    chromosome=variant_spec.chrom,
                    position=variant_spec.pos,
                    region_type=self.genomic_annotator.get_region_type(
                        variant_spec.chrom, 
                        variant_spec.pos,
                        {}  # Would pass gene annotations here
                    ),
                    gene_name=mutation.get('gene', 'Unknown'),
                    is_coding=self.genomic_annotator.is_coding_variant(
                        mutation.get('protein_change')
                    ),
                    genome_build="hg38"
                )
                
                # Use scientific detector
                scientific_result = self.scientific_detector.detect(
                    alphagenome_data=ag_result,
                    genomic_context=genomic_context,
                    tissue_type=self._get_tissue_name(tissue_ontology_id)
                )
                
                # Convert to analysis format
                enhancer_analysis = {
                    "scientific_detection": scientific_result.to_report_dict(),
                    "is_enhancer_like": scientific_result.is_enhancer,
                    "confidence": scientific_result.confidence,
                    "enhancer_state": scientific_result.enhancer_state.value,
                    "positive_marks_count": len(scientific_result.positive_marks),
                    "evidence_lines": scientific_result.positive_marks,
                    "warnings": scientific_result.warnings,
                    "interpretation": scientific_result.interpretation,
                    "detailed_scores": {
                        "histone": scientific_result.histone_score,
                        "accessibility": scientific_result.accessibility_score,
                        "rna": scientific_result.rna_score,
                        "statistical": scientific_result.statistical_significance
                    }
                }
                
                # Also run legacy detector for comparison
                legacy_result = self.enhancer_detector.detect(
                    ag_result["summary"], 
                    tissue_ontology_id
                )
                enhancer_analysis["legacy_detection"] = {
                    "is_enhancer_like": legacy_result.is_detected,
                    "confidence": legacy_result.confidence.value
                }
            else:
                # Use legacy detection
                detection_result = self.enhancer_detector.detect(
                    ag_result["summary"], 
                    tissue_ontology_id
                )
                
                # Also run legacy analysis for comparison
                legacy_analysis = self._analyze_enhancer_signatures(ag_result)
                
                # Combine results
                enhancer_analysis = {
                    "professional_detection": {
                        "is_enhancer_like": detection_result.is_detected,
                        "confidence": detection_result.confidence.value,
                        "algorithm_used": detection_result.algorithm_used.value,
                        "criteria_used": detection_result.criteria_used,
                        "positive_marks": detection_result.positive_marks,
                        "evidence_scores": detection_result.evidence_scores,
                        "total_evidence_score": detection_result.total_evidence_score,
                        "interpretation": detection_result.interpretation
                    },
                    "legacy_detection": legacy_analysis,
                    # Use professional detection as primary result
                    "is_enhancer_like": detection_result.is_detected,
                    "confidence": detection_result.confidence.value,
                    "positive_marks_count": len(detection_result.positive_marks),
                    "evidence_lines": [f"{mark}: {detection_result.evidence_scores.get(mark.lower().split('_')[0], 0):.3f}" for mark in detection_result.positive_marks],
                    "detailed_scores": detection_result.evidence_scores
                }
            
            return {
                "status": "success",
                "mutation": mutation,
                "variant": ag_result["variant"],
                "tissue_ontology": tissue_ontology_id,
                "alphagenome_result": ag_result,
                "enhancer_analysis": enhancer_analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"   ❌ Analysis failed: {e}")
            return {
                "status": "failed",
                "mutation": mutation,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _analyze_enhancer_signatures(self, ag_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Legacy enhancer analysis for comparison with professional detection.
        
        Returns:
            Dict with legacy enhancer detection results
        """
        summary = ag_result.get("summary", {})
        evidence_lines = []
        positive_marks = 0
        
        # Check DNase accessibility (open chromatin)
        dnase_data = summary.get("dnase", {})
        dnase_increase = dnase_data.get("max_increase", 0)
        if dnase_increase >= self.enhancer_criteria["dnase_min_increase"]:
            evidence_lines.append(f"DNase accessibility ↑{dnase_increase:.4f}")
            positive_marks += 1
        
        # Check histone marks
        histone_data = summary.get("chip_histone", {}).get("marks", {})
        
        # H3K27ac - active enhancer mark
        h3k27ac = histone_data.get("H3K27ac", {})
        h3k27ac_increase = h3k27ac.get("max_increase", 0)
        if h3k27ac_increase >= self.enhancer_criteria["h3k27ac_min_increase"]:
            evidence_lines.append(f"H3K27ac (active enhancer) ↑{h3k27ac_increase:.4f}")
            positive_marks += 1
        
        # H3K4me1 - enhancer mark
        h3k4me1 = histone_data.get("H3K4me1", {})
        h3k4me1_increase = h3k4me1.get("max_increase", 0)
        if h3k4me1_increase >= self.enhancer_criteria["h3k4me1_min_increase"]:
            evidence_lines.append(f"H3K4me1 (enhancer mark) ↑{h3k4me1_increase:.4f}")
            positive_marks += 1
        
        # Check RNA expression
        rna_data = summary.get("rna_seq", {})
        rna_increase = rna_data.get("max_increase", 0)
        if rna_increase >= self.enhancer_criteria["rna_min_increase"]:
            evidence_lines.append(f"RNA expression ↑{rna_increase:.6f}")
            positive_marks += 1
        
        # Make enhancer call based on legacy criteria
        is_enhancer_like = positive_marks >= self.enhancer_criteria["min_marks_required"]
        
        confidence = "high" if positive_marks >= 3 else "medium" if positive_marks == 2 else "low"
        
        return {
            "is_enhancer_like": is_enhancer_like,
            "confidence": confidence,
            "positive_marks_count": positive_marks,
            "evidence_lines": evidence_lines,
            "detailed_scores": {
                "dnase_increase": dnase_increase,
                "h3k27ac_increase": h3k27ac_increase,
                "h3k4me1_increase": h3k4me1_increase,
                "rna_increase": rna_increase
            },
            "criteria_used": "Legacy criteria",
            "method": "legacy"
        }
    
    def create_visualizations(self, analysis_result: Dict[str, Any]) -> List[str]:
        """
        Deprecated: Visualizations are now embedded in HTML reports.
        Kept for compatibility but returns empty list.
        """
        return []
    
    def generate_report(
        self,
        mutation_data: Dict[str, Any],
        analysis_results: List[Dict[str, Any]],
        research_question: str,
    ) -> str:
        """
        Generate interactive HTML report with Chart.js visualizations.
        
        Args:
            mutation_data: Raw mutation data from cBioPortal
            analysis_results: List of analysis results
            research_question: The research question being addressed
            
        Returns:
            Path to generated HTML report file
        """
        try:
            # Prepare results for Chart.js visualization
            prepared_results = []
            for result in analysis_results:
                if result.get("status") == "success":
                    prepared_result = {
                        "status": "success",
                        "variant_id": result.get("variant", "Unknown"),
                        "enhancer_detected": result.get("enhancer_analysis", {}).get("is_enhancer_like", False),
                        "detection_result": result.get("enhancer_analysis", {}),
                        "alphagenome_result": result.get("alphagenome_result", {})
                    }
                    prepared_results.append(prepared_result)
            
            # Generate HTML report with embedded Chart.js visualizations
            report_file = self.report_generator.generate_html_report(
                results=prepared_results,
                gene=mutation_data.get("gene", "Unknown"),
                cancer_type=mutation_data.get("cancer_type", "Unknown"),
                research_question=research_question,
                genome_build="hg38",  # AlphaGenome uses hg38
                tissue_type=self._get_tissue_name(mutation_data.get("tissue_ontology_id", "UBERON:0001264"))
            )
            
            return report_file
            
        except Exception as e:
            print(f"❌ Report generation failed: {e}")
            return ""
    
    def _create_analysis_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create summary of enhancer analysis results."""
        successful_results = [r for r in results if r.get("status") == "success"]
        enhancer_results = [
            r for r in successful_results 
            if r.get("enhancer_analysis", {}).get("is_enhancer_like", False)
        ]
        
        return {
            "total_mutations": len(results),
            "successfully_analyzed": len(successful_results),
            "enhancer_like_mutations": len(enhancer_results),
            "enhancer_detection_rate": len(enhancer_results) / len(successful_results) if successful_results else 0,
            "confidence_distribution": self._analyze_confidence_distribution(successful_results)
        }
    
    def _analyze_confidence_distribution(self, results: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze confidence distribution of results."""
        confidence_counts = {"high": 0, "medium": 0, "low": 0}
        for result in results:
            confidence = result.get("enhancer_analysis", {}).get("confidence", "low")
            confidence_counts[confidence] += 1
        return confidence_counts
    
    def _map_tissue_to_alphagenome(self, tissue_ontology_id: str) -> str:
        """Map tissue ontology ID to AlphaGenome tissue name."""
        mapping = {
            "UBERON:0000310": "breast",
            "UBERON:0001264": "pancreatic",
            "UBERON:0002048": "lung",
            "UBERON:0001157": "colorectal"
        }
        return mapping.get(tissue_ontology_id, "pancreatic")  # Default to pancreatic
    
    def _get_tissue_name(self, tissue_ontology_id: str) -> str:
        """Get human-readable tissue name from ontology ID."""
        name_mapping = {
            "UBERON:0000310": "Breast",
            "UBERON:0001264": "Pancreatic", 
            "UBERON:0002048": "Lung",
            "UBERON:0001157": "Colorectal",
            "UBERON:0000955": "Brain",
            "UBERON:0002367": "Prostate"
        }
        return name_mapping.get(tissue_ontology_id, "Unknown")
    
    def _make_research_question(self, gene: str, cancer_type: str) -> str:
        """Generate specific research question for enhancer detection."""
        return f"Do {gene} mutations create enhancer-like regulatory elements in {cancer_type} cancer?"
    
    def _summarize(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create enhancer-specific summary statistics."""
        base_summary = super()._summarize(results)
        
        successful_results = [r for r in results if r.get("status") == "success"]
        enhancer_results = [
            r for r in successful_results 
            if r.get("enhancer_analysis", {}).get("is_enhancer_like", False)
        ]
        
        base_summary.update({
            "enhancers_detected": len(enhancer_results),
            "enhancer_detection_rate": len(enhancer_results) / len(successful_results) if successful_results else 0,
            "high_confidence_enhancers": len([
                r for r in enhancer_results 
                if r.get("enhancer_analysis", {}).get("confidence") == "high"
            ])
        })
        
        return base_summary
    
    def _print_answer_line(self, summary: Dict[str, Any]) -> None:
        """Print enhancer detection answer line."""
        enhancers_detected = summary.get("enhancers_detected", 0)
        total_analyzed = summary.get("mutations_analyzed", 0)
        
        if enhancers_detected == 0:
            print("❌ ANSWER: NO enhancer-like mutations detected")
        elif enhancers_detected == total_analyzed:
            print(f"✅ ANSWER: YES - All {total_analyzed} mutations show enhancer-like signatures")
        else:
            rate = summary.get("enhancer_detection_rate", 0) * 100
            print(f"⚠️ ANSWER: PARTIAL - {enhancers_detected}/{total_analyzed} mutations ({rate:.1f}%) show enhancer-like signatures")
        
        print(f"\n🖼️ Visualizations: Interactive Chart.js embedded in HTML report")


def main():
    """CLI entry point for enhancer detection pipeline."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Professional Enhancer Detection Pipeline")
    parser.add_argument("--gene", required=True, help="Gene symbol (e.g., KRAS)")
    parser.add_argument("--cancer", required=True, help="Cancer type (e.g., pancreatic)")
    parser.add_argument("--max-mutations", type=int, default=10, help="Maximum mutations to analyze")
    parser.add_argument("--output-dir", default="data/enhancer_outputs", help="Output directory")
    parser.add_argument("--api-key", help="AlphaGenome API key (or set ALPHAGENOME_API_KEY)")
    parser.add_argument("--algorithm", choices=["conservative", "balanced", "sensitive"], 
                       default="balanced", help="Detection algorithm (default: balanced)")
    
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or os.environ.get("ALPHAGENOME_API_KEY")
    if not api_key:
        print("❌ AlphaGenome API key required. Set ALPHAGENOME_API_KEY or use --api-key")
        return 1
    
    # Convert algorithm string to enum
    algorithm_map = {
        "conservative": DetectionAlgorithm.CONSERVATIVE,
        "balanced": DetectionAlgorithm.BALANCED,
        "sensitive": DetectionAlgorithm.SENSITIVE
    }
    
    # Run pipeline with professional detection
    pipeline = EnhancerDetectionPipeline(
        alphagenome_api_key=api_key,
        output_dir=args.output_dir,
        detection_algorithm=algorithm_map[args.algorithm]
    )
    
    print(f"🔬 Using {args.algorithm} detection algorithm")
    print(f"📊 Algorithm: {DetectorFactory.get_algorithm_description(algorithm_map[args.algorithm])}")
    print(f"🔬 Criteria: {pipeline.enhancer_detector.get_criteria_name()}\n")
    
    result = pipeline.run(
        gene=args.gene,
        cancer_type=args.cancer,
        max_mutations=args.max_mutations
    )
    
    # Print results
    print("\n" + "="*80)
    print("📊 PIPELINE RESULTS")
    print("="*80)
    print(json.dumps(result, indent=2, default=str))
    
    return 0 if result.get("status") == "success" else 1


if __name__ == "__main__":
    exit(main())