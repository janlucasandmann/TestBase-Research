from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime

try:
    from .renderer import ReportRenderer, VariantEntry, FigureSpec
except ImportError:
    # Fallback for when renderer is not available
    ReportRenderer = None
    VariantEntry = None
    FigureSpec = None


class ReportGenerator:
    """Professional report generator for enhancer detection pipeline."""
    """
    Thin adapter used by the EnhancerPipeline.
    Consumes raw mutation_data + analysis_results and renders a portable HTML report
    via the generic ReportRenderer.
    """

    def __init__(self, *, output_dir: str = "data/reports", title: str = "Enhancer Detection Report (AlphaGenome)") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.title = title
        self.renderer = ReportRenderer(title=title) if ReportRenderer else None

    def generate_enhancer_report(self, report_data: Dict[str, Any]) -> str:
        """Generate an enhancer detection report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create both JSON and Markdown reports for maximum compatibility
        json_file = self._generate_json_report(report_data, timestamp)
        md_file = self._generate_markdown_report(report_data, timestamp)
        
        # If HTML renderer is available, create HTML report too
        if self.renderer:
            html_file = self._generate_html_report(report_data, timestamp)
            return html_file
        else:
            return md_file
    
    def _generate_json_report(self, report_data: Dict[str, Any], timestamp: str) -> str:
        """Generate JSON report for machine readability."""
        filename = f"enhancer_report_{timestamp}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        return str(filepath)
    
    def _generate_markdown_report(self, report_data: Dict[str, Any], timestamp: str) -> str:
        """Generate Markdown report for human readability."""
        filename = f"enhancer_report_{timestamp}.md"
        filepath = self.output_dir / filename
        
        content = self._build_markdown_content(report_data)
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        return str(filepath)
    
    def _build_markdown_content(self, data: Dict[str, Any]) -> str:
        """Build markdown content from report data."""
        lines = []
        
        # Header
        lines.append(f"# {self.title}")
        lines.append(f"\n**Generated:** {data.get('timestamp', 'Unknown')}")
        lines.append(f"**Pipeline Version:** {data.get('pipeline_version', '1.0.0')}")
        lines.append("\n---\n")
        
        # Research Question
        lines.append("## Research Question")
        lines.append(f"{data.get('research_question', 'Unknown')}\n")
        
        # Summary
        summary = data.get('analysis_summary', {})
        lines.append("## Analysis Summary")
        lines.append(f"- **Gene:** {data.get('gene', 'Unknown')}")
        lines.append(f"- **Cancer Type:** {data.get('cancer_type', 'Unknown')}")
        lines.append(f"- **Total Mutations:** {summary.get('total_mutations', 0)}")
        lines.append(f"- **Successfully Analyzed:** {summary.get('successfully_analyzed', 0)}")
        lines.append(f"- **Enhancer-like Mutations:** {summary.get('enhancer_like_mutations', 0)}")
        lines.append(f"- **Detection Rate:** {summary.get('enhancer_detection_rate', 0):.2%}")
        lines.append("")
        
        # Answer
        enhancer_count = summary.get('enhancer_like_mutations', 0)
        total_count = summary.get('successfully_analyzed', 0)
        
        lines.append("## Answer")
        if enhancer_count == 0:
            lines.append("❌ **NO** - No enhancer-like mutations detected")
        elif enhancer_count == total_count and total_count > 0:
            lines.append(f"✅ **YES** - All {total_count} mutations show enhancer-like signatures")
        else:
            rate = (enhancer_count / total_count * 100) if total_count > 0 else 0
            lines.append(f"⚠️ **PARTIAL** - {enhancer_count}/{total_count} mutations ({rate:.1f}%) show enhancer-like signatures")
        lines.append("")
        
        # Criteria
        criteria = data.get('enhancer_criteria', {})
        lines.append("## Enhancer Detection Criteria")
        for key, value in criteria.items():
            lines.append(f"- **{key}:** {value}")
        lines.append("")
        
        # Detailed Results
        results = data.get('detailed_results', [])
        lines.append("## Detailed Results")
        
        for i, result in enumerate(results, 1):
            if result.get('status') != 'success':
                continue
                
            mutation = result.get('mutation', {})
            variant = result.get('variant', '')
            enhancer = result.get('enhancer_analysis', {})
            
            lines.append(f"### Mutation {i}: {variant}")
            lines.append(f"- **Status:** {result.get('status')}")
            lines.append(f"- **Enhancer-like:** {'Yes' if enhancer.get('is_enhancer_like') else 'No'}")
            lines.append(f"- **Confidence:** {enhancer.get('confidence', 'Unknown')}")
            lines.append(f"- **Positive Marks:** {enhancer.get('positive_marks_count', 0)}")
            
            evidence = enhancer.get('evidence_lines', [])
            if evidence:
                lines.append("- **Evidence:**")
                for ev in evidence:
                    lines.append(f"  - {ev}")
            
            lines.append("")
        
        # Methods
        lines.append("## Methods")
        lines.append("1. **Data Source:** Real mutation data from cBioPortal")
        lines.append("2. **Analysis:** AlphaGenome API for regulatory predictions")
        lines.append("3. **Window Size:** 131,072 bp (128kb) for long-range effects")
        lines.append("4. **Tissue Context:** Mapped to appropriate tissue ontology")
        lines.append("")
        
        # Limitations
        lines.append("## Limitations")
        lines.append("- Computational predictions require experimental validation")
        lines.append("- Tissue-specific effects may vary from in vivo conditions")
        lines.append("- Limited to sequence context within analysis window")
        lines.append("- Structural variants beyond SNVs not fully captured")
        
        return "\n".join(lines)
    
    def _generate_html_report(self, report_data: Dict[str, Any], timestamp: str) -> str:
        """Generate HTML report if renderer is available."""
        if not self.renderer:
            return ""
        
        # Convert data to renderer format
        mutation_data = report_data.get('mutation_data', {})
        analysis_results = report_data.get('detailed_results', [])
        research_question = report_data.get('research_question', '')
        
        filename = f"enhancer_report_{timestamp}.html"
        out_dir = self.output_dir
        
        try:
            # Build VariantEntry list if renderer classes are available
            variants: List[VariantEntry] = []
            for item in analysis_results:
                mut = item.get("mutation", {}) or item.get("variant", {})
                chrom = str(mut.get("chromosome", mut.get("chrom", "chr?")))
                pos = int(mut.get("position", mut.get("pos", 0)) or 0)
                ref = str(mut.get("ref", "?"))
                alt = str(mut.get("alt", "?"))
                variant_id = f"{chrom}:{pos}:{ref}>{alt}"

                figs: List[FigureSpec] = []
                for p in item.get("visualizations", []) or []:
                    figs.append(FigureSpec(caption=Path(p).name, path=Path(p)))

                enhancer_analysis = item.get("enhancer_analysis", {})
                enhancers_detected = 1 if enhancer_analysis.get("is_enhancer_like", False) else 0
                
                variants.append(
                    VariantEntry(
                        variant_id=variant_id,
                        chrom=chrom,
                        pos=pos,
                        ref=ref,
                        alt=alt,
                        status=item.get("status", "unknown"),
                        enhancers_detected=enhancers_detected,
                        notes=f"Confidence: {enhancer_analysis.get('confidence', 'Unknown')}",
                        figures=figs,
                        modality_deltas=enhancer_analysis.get("detailed_scores", {}),
                    )
                )

            # Compute summary
            successful = [r for r in analysis_results if r.get("status") == "success"]
            enhancer_positive_variants = sum(1 for r in successful if r.get("enhancer_analysis", {}).get("is_enhancer_like", False))
            summary: Dict[str, Any] = {
                "mutations_analyzed": len(successful),
                "enhancer_positive_variants": enhancer_positive_variants,
                "answer_yes": enhancer_positive_variants > 0,
                "yes_details": f"{enhancer_positive_variants} enhancer-like mutation(s) detected" if enhancer_positive_variants > 0 else "",
            }

            # Meta
            meta: Dict[str, Any] = {
                "research_question": research_question,
                "gene": mutation_data.get("gene", ""),
                "cancer_type": mutation_data.get("cancer_type", ""),
                "methods": [
                    "Pulled real mutations from cBioPortal for the selected gene and cancer type.",
                    "Scored enhancer-related signals with AlphaGenome (DNase, histone marks, RNA expression).",
                    "Applied evidence-based criteria for enhancer detection.",
                ],
                "limitations": [
                    "AlphaGenome predictions are computational and require wet-lab validation.",
                    "Reported effects may vary across cell types; we approximate with the closest tissue.",
                    "Structural variants and long-range rearrangements beyond the context window are not fully evaluated.",
                ],
            }

            # Render + save
            html = self.renderer.build_html(meta=meta, variants=variants, summary=summary)
            out_path = out_dir / filename
            self.renderer.save(html, out_path)
            return str(out_path)
            
        except Exception as e:
            print(f"HTML report generation failed: {e}")
            # Fallback to markdown
            return self._generate_markdown_report(report_data, timestamp)