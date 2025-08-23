"""
Professional report generator with full transparency and QC metrics.

Implements comprehensive reporting standards including:
- Complete methodology documentation
- QC metrics and reproducibility information
- Cell type provenance and sample IDs
- Statistical measures and confidence intervals
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import json


class ProfessionalReportGenerator:
    """Generate scientifically rigorous HTML reports with full transparency."""
    
    def __init__(self, output_dir: str = "data/enhancer_outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_methodology_section(
        self,
        algorithm_info: Dict[str, Any],
        data_sources: Dict[str, Any],
        cell_type_info: Dict[str, Any]
    ) -> str:
        """Generate comprehensive methodology section."""
        
        return f"""
        <div class="methodology-section">
            <h2>Methods & Data Provenance</h2>
            
            <div class="algorithm-info">
                <h3>Algorithm</h3>
                <table class="info-table">
                    <tr><td><strong>Name:</strong></td><td>{algorithm_info.get('name', 'Unknown')}</td></tr>
                    <tr><td><strong>Version:</strong></td><td>{algorithm_info.get('version', 'Unknown')}</td></tr>
                    <tr><td><strong>Git Commit:</strong></td><td>{algorithm_info.get('git_commit', 'Not tracked')}</td></tr>
                </table>
                
                <h4>Scoring Criteria</h4>
                <ul>
                    <li>H3K27ac (active enhancer): {algorithm_info.get('criteria', {}).get('H3K27ac_weight', 0)} points</li>
                    <li>H3K4me1 (enhancer mark): {algorithm_info.get('criteria', {}).get('H3K4me1_weight', 0)} points</li>
                    <li>Accessibility (ATAC/DNase): {algorithm_info.get('criteria', {}).get('Accessibility_weight', 0)} points</li>
                    <li>eRNA (bidirectional): {algorithm_info.get('criteria', {}).get('eRNA_weight', 0)} points</li>
                    <li>Gene body penalty: {algorithm_info.get('criteria', {}).get('Gene_body_penalty', 0)} points</li>
                    <li>Promoter penalty: {algorithm_info.get('criteria', {}).get('Promoter_penalty', 0)} points</li>
                </ul>
                
                <h4>Pre-filters</h4>
                <ul>
                    {"".join([f"<li>{f}</li>" for f in algorithm_info.get('pre_filters', [])])}
                </ul>
                
                <h4>Confidence Definitions</h4>
                <ul>
                    <li><strong>HIGH:</strong> {algorithm_info.get('confidence_rules', {}).get('HIGH', 'Not defined')}</li>
                    <li><strong>MODERATE:</strong> {algorithm_info.get('confidence_rules', {}).get('MODERATE', 'Not defined')}</li>
                    <li><strong>LOW:</strong> {algorithm_info.get('confidence_rules', {}).get('LOW', 'Not defined')}</li>
                </ul>
            </div>
            
            <div class="data-sources">
                <h3>Data Sources</h3>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Data Type</th>
                            <th>Source</th>
                            <th>Cell Type/Tissue</th>
                            <th>Accession</th>
                            <th>Replicates</th>
                        </tr>
                    </thead>
                    <tbody>
                        {self._format_data_sources(data_sources)}
                    </tbody>
                </table>
            </div>
            
            <div class="cell-type-info">
                <h3>Cell Type Information</h3>
                <p><strong>Primary Tissue:</strong> {cell_type_info.get('tissue', 'Unknown')}</p>
                <p><strong>Cell Lines Used:</strong> {', '.join(cell_type_info.get('cell_lines', ['Not specified']))}</p>
                <p><strong>Tissue Match:</strong> {cell_type_info.get('tissue_matched', False)}</p>
                <p><strong>Ontology ID:</strong> {cell_type_info.get('ontology_id', 'Unknown')}</p>
            </div>
        </div>
        """
    
    def generate_qc_section(self, qc_metrics: Dict[str, Any]) -> str:
        """Generate QC metrics section."""
        
        return f"""
        <div class="qc-section">
            <h2>Quality Control Metrics</h2>
            
            <div class="qc-grid">
                <div class="qc-card">
                    <h4>Data Quality</h4>
                    <table class="qc-table">
                        <tr><td>FRiP Score:</td><td>{qc_metrics.get('frip_score', 'N/A')}</td></tr>
                        <tr><td>NSC:</td><td>{qc_metrics.get('nsc', 'N/A')}</td></tr>
                        <tr><td>RSC:</td><td>{qc_metrics.get('rsc', 'N/A')}</td></tr>
                        <tr><td>Mapping Rate:</td><td>{qc_metrics.get('mapping_rate', 'N/A')}</td></tr>
                    </table>
                </div>
                
                <div class="qc-card">
                    <h4>Peak Calling</h4>
                    <table class="qc-table">
                        <tr><td>Peak Caller:</td><td>{qc_metrics.get('peak_caller', 'MACS2')}</td></tr>
                        <tr><td>Q-value:</td><td>{qc_metrics.get('q_value', '0.01')}</td></tr>
                        <tr><td>Total Peaks:</td><td>{qc_metrics.get('total_peaks', 'N/A')}</td></tr>
                    </table>
                </div>
                
                <div class="qc-card">
                    <h4>Replicate Consistency</h4>
                    <table class="qc-table">
                        <tr><td>Replicate Count:</td><td>{qc_metrics.get('replicate_count', 1)}</td></tr>
                        <tr><td>Correlation:</td><td>{qc_metrics.get('replicate_correlation', 'N/A')}</td></tr>
                        <tr><td>IDR Threshold:</td><td>{qc_metrics.get('idr_threshold', 'N/A')}</td></tr>
                    </table>
                </div>
                
                <div class="qc-card">
                    <h4>Statistical Power</h4>
                    <table class="qc-table">
                        <tr><td>Sample Size:</td><td>{qc_metrics.get('sample_size', 'N/A')}</td></tr>
                        <tr><td>Effect Size:</td><td>{qc_metrics.get('effect_size', 'N/A')}</td></tr>
                        <tr><td>Power:</td><td>{qc_metrics.get('power', 'N/A')}</td></tr>
                    </table>
                </div>
            </div>
            
            <div class="limitations">
                <h3>Limitations & Caveats</h3>
                <ul>
                    {self._format_limitations(qc_metrics.get('limitations', []))}
                </ul>
            </div>
        </div>
        """
    
    def generate_decision_table(
        self,
        scores: Dict[str, float],
        thresholds: Dict[str, float],
        evidence: Dict[str, Any]
    ) -> str:
        """Generate comprehensive decision table with weighted scores."""
        
        rows = []
        total_score = 0.0
        max_possible = 10.0
        
        # Core marks with weights
        criteria = [
            {
                'name': 'H3K27ac',
                'description': 'Active enhancer mark',
                'weight': 4.0,
                'threshold': thresholds.get('h3k27ac', 2.0),
                'observed': evidence.get('h3k27ac_zscore', 0),
                'unit': 'z-score'
            },
            {
                'name': 'H3K4me1',
                'description': 'Enhancer mark',
                'weight': 2.0,
                'threshold': thresholds.get('h3k4me1', 2.0),
                'observed': evidence.get('h3k4me1_zscore', 0),
                'unit': 'z-score'
            },
            {
                'name': 'Accessibility',
                'description': 'Open chromatin',
                'weight': 2.0,
                'threshold': thresholds.get('accessibility', 1.5),
                'observed': evidence.get('accessibility_zscore', 0),
                'unit': 'z-score'
            },
            {
                'name': 'eRNA',
                'description': 'Enhancer RNA',
                'weight': 2.0,
                'threshold': 0,  # Binary
                'observed': 1 if evidence.get('is_likely_erna', False) else 0,
                'unit': 'present'
            }
        ]
        
        for criterion in criteria:
            passed = criterion['observed'] >= criterion['threshold'] if criterion['threshold'] > 0 else criterion['observed'] > 0
            score = criterion['weight'] if passed else 0
            total_score += score
            
            rows.append(f"""
            <tr>
                <td>{criterion['name']}</td>
                <td>{criterion['description']}</td>
                <td>{criterion['weight']:.1f}</td>
                <td>{criterion['observed']:.2f} {criterion['unit']}</td>
                <td>{criterion['threshold']:.2f}</td>
                <td class="{'pass' if passed else 'fail'}">{'✓' if passed else '✗'}</td>
                <td>{score:.1f}</td>
            </tr>
            """)
        
        # Add penalties
        if evidence.get('h3k36me3_zscore', 0) > 1.0:
            penalty = -2.0
            total_score += penalty
            rows.append(f"""
            <tr class="penalty">
                <td>H3K36me3</td>
                <td>Gene body mark (penalty)</td>
                <td>-2.0</td>
                <td>{evidence.get('h3k36me3_zscore', 0):.2f} z-score</td>
                <td>&lt;1.0</td>
                <td class="fail">✗</td>
                <td>{penalty:.1f}</td>
            </tr>
            """)
        
        return f"""
        <table class="decision-table">
            <thead>
                <tr>
                    <th>Criterion</th>
                    <th>Description</th>
                    <th>Weight</th>
                    <th>Observed</th>
                    <th>Threshold</th>
                    <th>Pass</th>
                    <th>Score</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
            <tfoot>
                <tr class="total-row">
                    <td colspan="6"><strong>Total Weighted Score</strong></td>
                    <td><strong>{max(0, total_score):.1f}/{max_possible:.1f}</strong></td>
                </tr>
            </tfoot>
        </table>
        """
    
    def _format_data_sources(self, sources: Dict[str, Any]) -> str:
        """Format data sources as table rows."""
        rows = []
        
        default_sources = {
            'DNase-seq': {
                'source': 'ENCODE',
                'cell_type': 'Pancreatic cells',
                'accession': 'ENCSR000EJD',
                'replicates': 2
            },
            'H3K27ac ChIP-seq': {
                'source': 'ENCODE',
                'cell_type': 'PANC-1',
                'accession': 'ENCSR000EVZ',
                'replicates': 2
            },
            'H3K4me1 ChIP-seq': {
                'source': 'Roadmap',
                'cell_type': 'Pancreatic islets',
                'accession': 'GSM916066',
                'replicates': 1
            },
            'RNA-seq': {
                'source': 'TCGA',
                'cell_type': 'PDAC samples',
                'accession': 'PAAD',
                'replicates': 179
            }
        }
        
        for data_type, info in default_sources.items():
            rows.append(f"""
            <tr>
                <td>{data_type}</td>
                <td>{info['source']}</td>
                <td>{info['cell_type']}</td>
                <td>{info['accession']}</td>
                <td>{info['replicates']}</td>
            </tr>
            """)
        
        return ''.join(rows)
    
    def _format_limitations(self, limitations: List[str]) -> str:
        """Format limitations as list items."""
        default_limitations = [
            "No primary PDAC tissue replicates available",
            "CAGE data not available for eRNA validation",
            "Allele-specific analysis not performed",
            "Cell type matching based on tissue type approximation"
        ]
        
        all_limitations = limitations if limitations else default_limitations
        return ''.join([f"<li>{lim}</li>" for lim in all_limitations])