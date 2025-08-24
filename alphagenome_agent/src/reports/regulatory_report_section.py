"""
Advanced regulatory assessment report section.

Replaces simplistic numeric scores with biologically meaningful assessments
that provide actionable insights for researchers.
"""

from typing import Dict, Any
from ..scoring.regulatory_assessment import RegulatoryAssessmentEngine, RegulatoryClass, EvidenceStrength


class RegulatoryReportSection:
    """Generate advanced regulatory assessment report sections."""
    
    def __init__(self):
        self.assessment_engine = RegulatoryAssessmentEngine()
    
    def generate_assessment_section(
        self,
        alphagenome_result: Dict[str, Any],
        genomic_context: Dict[str, Any],
        variant_id: str
    ) -> str:
        """
        Generate comprehensive regulatory assessment section.
        
        Args:
            alphagenome_result: AlphaGenome API results
            genomic_context: Genomic context information
            variant_id: Variant identifier
            
        Returns:
            HTML section with comprehensive assessment
        """
        
        # Perform assessment
        assessment = self.assessment_engine.assess_variant(
            alphagenome_result, genomic_context, variant_id
        )
        
        # Generate HTML sections
        gateway_section = self._generate_gateway_decision_section(assessment, genomic_context)
        classification_section = self._generate_classification_section(assessment)
        evidence_section = self._generate_evidence_section(assessment)
        interpretation_section = self._generate_interpretation_section(assessment)
        actionable_section = self._generate_actionable_insights_section(assessment)
        quality_section = self._generate_quality_assessment_section(assessment)
        
        return f"""
        <div class="regulatory-assessment">
            <h2>Regulatory Assessment</h2>
            <p class="assessment-subtitle">
                Biologically-informed analysis replacing arbitrary numeric scores
            </p>
            
            {gateway_section}
            {classification_section}
            {evidence_section}
            {interpretation_section}
            {actionable_section}
            {quality_section}
        </div>
        """
    
    def _generate_gateway_decision_section(self, assessment, genomic_context: Dict[str, Any]) -> str:
        """Generate gateway decision section that precedes scoring."""
        
        # Determine if this is a gene-proximal region
        is_gene_proximal = (
            genomic_context.get('is_exon', False) or 
            genomic_context.get('is_coding', False) or
            genomic_context.get('distance_to_tss', float('inf')) < 2000
        )
        
        if is_gene_proximal:
            return f"""
            <div class="gateway-decision">
                <div class="gateway-header">
                    <span class="gateway-icon">🚦</span>
                    <h3>Gateway Decision</h3>
                </div>
                <div class="gateway-content">
                    <div class="gateway-badge not-applicable">
                        <span class="badge-icon">🔴</span>
                        <span class="badge-text">Not Applicable - Gene Proximal Region</span>
                    </div>
                    <div class="gateway-explanation">
                        <p><strong>Decision Rationale:</strong></p>
                        <ul>
                            <li>Location: {genomic_context.get('region_type', 'Coding region')}</li>
                            <li>Gene: {genomic_context.get('gene', 'Unknown')} {f"Exon {genomic_context.get('exon_number')}" if genomic_context.get('exon_number') else ""}</li>
                            <li>Assessment: Enhancer detection not applicable for gene-proximal variants</li>
                        </ul>
                        <p class="gateway-note">
                            <strong>Note:</strong> Chromatin signals shown below reflect gene body activity 
                            and are <em>not counted</em> toward enhancer classification. For coding variants, 
                            focus on protein-level effects rather than regulatory interpretation.
                        </p>
                    </div>
                </div>
            </div>
            """
        else:
            # Non-gene-proximal: proceed with standard assessment
            data_quality = "High" if genomic_context.get('tissue_matched', False) else "Moderate"
            return f"""
            <div class="gateway-decision">
                <div class="gateway-header">
                    <span class="gateway-icon">🚦</span>
                    <h3>Gateway Decision</h3>
                </div>
                <div class="gateway-content">
                    <div class="gateway-badge proceed">
                        <span class="badge-icon">🟢</span>
                        <span class="badge-text">Proceed - Intergenic/Intronic Region</span>
                    </div>
                    <div class="gateway-explanation">
                        <p><strong>Assessment Criteria:</strong></p>
                        <ul>
                            <li>Location suitable for enhancer assessment</li>
                            <li>Data quality: {data_quality}</li>
                            <li>Chromatin marks will be evaluated for regulatory potential</li>
                        </ul>
                    </div>
                </div>
            </div>
            """
    
    def _generate_classification_section(self, assessment) -> str:
        """Generate regulatory classification section."""
        
        # Color coding for different classifications
        class_colors = {
            "active_enhancer": "#00a699",
            "primed_enhancer": "#ffb400", 
            "weak_enhancer": "#ff9500",
            "promoter_like": "#008489",
            "gene_body": "#717171",
            "not_applicable": "#dc3545",
            "quiescent": "#a0a0a0",
            "ambiguous": "#6c757d"
        }
        
        # Icons for classifications
        class_icons = {
            "active_enhancer": "🟢",
            "primed_enhancer": "🟡",
            "weak_enhancer": "🟠", 
            "promoter_like": "🔵",
            "gene_body": "⚪",
            "not_applicable": "🔴",
            "quiescent": "⚫",
            "ambiguous": "🔘"
        }
        
        reg_class = assessment.regulatory_class
        color = class_colors.get(reg_class.value, "#6c757d")
        icon = class_icons.get(reg_class.value, "❓")
        
        # Evidence strength styling
        strength_colors = {
            "strong": "#28a745",
            "moderate": "#ffc107", 
            "weak": "#fd7e14",
            "conflicting": "#dc3545",
            "insufficient": "#6c757d"
        }
        
        evidence_color = strength_colors.get(assessment.evidence_strength.value, "#6c757d")
        
        return f"""
        <div class="classification-section">
            <div class="classification-header">
                <div class="classification-badge" style="background: {color}20; color: {color}; border-left: 4px solid {color};">
                    <span class="classification-icon">{icon}</span>
                    <div class="classification-content">
                        <div class="classification-title">
                            {reg_class.value.replace('_', ' ').title()}
                        </div>
                        <div class="classification-subtitle">
                            {assessment.genomic_context}
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="evidence-strength-bar">
                <div class="evidence-label">Evidence Strength:</div>
                <div class="evidence-badge" style="background: {evidence_color}20; color: {evidence_color};">
                    {assessment.evidence_strength.value.title()}
                </div>
                <div class="confidence-badge">
                    {assessment.confidence_level}
                </div>
            </div>
        </div>
        """
    
    def _generate_evidence_section(self, assessment) -> str:
        """Generate detailed evidence section."""
        
        bio_evidence = assessment.biological_evidence
        
        # Create evidence cards
        evidence_cards = []
        
        # Chromatin accessibility
        acc_level = "Strong" if bio_evidence.chromatin_accessibility > 0.1 else \
                   "Moderate" if bio_evidence.chromatin_accessibility > 0.05 else "Weak"
        acc_color = "#28a745" if acc_level == "Strong" else "#ffc107" if acc_level == "Moderate" else "#dc3545"
        
        evidence_cards.append(f"""
        <div class="evidence-card">
            <div class="evidence-header">
                <span class="evidence-icon" style="background: {acc_color}20; color: {acc_color};">🔓</span>
                <div class="evidence-title">Chromatin Accessibility</div>
            </div>
            <div class="evidence-value">{bio_evidence.chromatin_accessibility:.4f}</div>
            <div class="evidence-interpretation">{acc_level} accessibility</div>
        </div>
        """)
        
        # Histone marks
        for mark, value in bio_evidence.active_marks.items():
            if value > 0:
                mark_level = "Present" if value > 0.05 else "Low"
                mark_color = "#00a699" if mark_level == "Present" else "#a0a0a0"
                
                mark_descriptions = {
                    'H3K27ac': 'Active enhancer mark',
                    'H3K4me1': 'Enhancer mark', 
                    'H3K4me3': 'Promoter mark',
                    'H3K36me3': 'Gene body mark'
                }
                
                evidence_cards.append(f"""
                <div class="evidence-card">
                    <div class="evidence-header">
                        <span class="evidence-icon" style="background: {mark_color}20; color: {mark_color};">🧬</span>
                        <div class="evidence-title">{mark}</div>
                    </div>
                    <div class="evidence-value">{value:.4f}</div>
                    <div class="evidence-interpretation">{mark_descriptions.get(mark, mark)}</div>
                </div>
                """)
        
        # Transcription
        if bio_evidence.transcription > 0:
            tx_level = "High" if bio_evidence.transcription > 0.01 else \
                      "Moderate" if bio_evidence.transcription > 0.001 else "Low"
            tx_color = "#ff5a5f" if tx_level == "High" else "#ffb400" if tx_level == "Moderate" else "#a0a0a0"
            
            evidence_cards.append(f"""
            <div class="evidence-card">
                <div class="evidence-header">
                    <span class="evidence-icon" style="background: {tx_color}20; color: {tx_color};">📊</span>
                    <div class="evidence-title">Transcription</div>
                </div>
                <div class="evidence-value">{bio_evidence.transcription:.6f}</div>
                <div class="evidence-interpretation">{tx_level} RNA signal</div>
            </div>
            """)
        
        return f"""
        <div class="evidence-section">
            <h3>Biological Evidence Profile</h3>
            <div class="evidence-grid">
                {''.join(evidence_cards)}
            </div>
        </div>
        """
    
    def _generate_interpretation_section(self, assessment) -> str:
        """Generate biological interpretation section."""
        
        return f"""
        <div class="interpretation-section">
            <h3>Biological Interpretation</h3>
            <div class="interpretation-content">
                <div class="primary-interpretation">
                    <h4>Primary Assessment</h4>
                    <p>{assessment.biological_interpretation}</p>
                </div>
                
                <div class="functional-prediction">
                    <h4>Functional Prediction</h4>
                    <p>{assessment.functional_prediction}</p>
                </div>
                
                <div class="target-genes">
                    <h4>Potential Target Genes</h4>
                    <div class="gene-list">
                        {', '.join(assessment.target_genes) if assessment.target_genes else 'To be determined'}
                    </div>
                </div>
                
                <div class="comparative-context">
                    <h4>Comparative Analysis</h4>
                    <p>{assessment.comparative_analysis}</p>
                </div>
            </div>
        </div>
        """
    
    def _generate_actionable_insights_section(self, assessment) -> str:
        """Generate actionable insights section."""
        
        # Format follow-up experiments
        experiment_list = ''.join([f"<li>{exp}</li>" for exp in assessment.follow_up_experiments])
        
        return f"""
        <div class="actionable-section">
            <h3>Actionable Insights</h3>
            
            <div class="insights-grid">
                <div class="insight-card">
                    <h4>🧪 Recommended Experiments</h4>
                    <ul class="experiment-list">
                        {experiment_list}
                    </ul>
                </div>
                
                <div class="insight-card">
                    <h4>🏥 Clinical Relevance</h4>
                    <p>{assessment.clinical_relevance}</p>
                </div>
            </div>
        </div>
        """
    
    def _generate_quality_assessment_section(self, assessment) -> str:
        """Generate quality assessment section."""
        
        # Format quality flags
        flags_html = ""
        if assessment.data_quality_flags:
            flag_items = ''.join([f"<li>⚠️ {flag}</li>" for flag in assessment.data_quality_flags])
            flags_html = f"""
            <div class="quality-flags">
                <h4>Data Quality Flags</h4>
                <ul>{flag_items}</ul>
            </div>
            """
        
        # Format limitations
        limitation_items = ''.join([f"<li>{lim}</li>" for lim in assessment.limitations])
        
        return f"""
        <div class="quality-section">
            <h3>Quality Assessment</h3>
            
            {flags_html}
            
            <div class="limitations">
                <h4>Analysis Limitations</h4>
                <ul class="limitation-list">
                    {limitation_items}
                </ul>
            </div>
            
            <div class="methodology-note">
                <p><strong>Note:</strong> This assessment uses evidence-based biological criteria 
                rather than arbitrary numeric scores to provide more meaningful regulatory insights.</p>
            </div>
        </div>
        """
    
    def get_css_styles(self) -> str:
        """Return CSS styles for the regulatory assessment section."""
        
        return """
        .gateway-decision {
            margin-bottom: 32px;
            padding: 20px;
            background: #f9fafb;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
        }
        
        .gateway-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 16px;
        }
        
        .gateway-icon {
            font-size: 20px;
        }
        
        .gateway-header h3 {
            font-size: 16px;
            font-weight: 600;
            color: var(--text-primary);
            margin: 0;
        }
        
        .gateway-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 500;
            margin-bottom: 16px;
        }
        
        .gateway-badge.not-applicable {
            background: #fee2e2;
            color: #dc2626;
            border: 1px solid #fca5a5;
        }
        
        .gateway-badge.proceed {
            background: #d1fae5;
            color: #065f46;
            border: 1px solid #6ee7b7;
        }
        
        .gateway-explanation {
            font-size: 14px;
            color: var(--text-secondary);
        }
        
        .gateway-explanation ul {
            margin: 8px 0;
            padding-left: 20px;
        }
        
        .gateway-explanation li {
            margin-bottom: 4px;
        }
        
        .gateway-note {
            margin-top: 12px;
            padding: 12px;
            background: #fef3c7;
            border-left: 3px solid #f59e0b;
            border-radius: 4px;
            font-size: 13px;
        }
        
        .regulatory-assessment {
            margin: 32px 0;
            padding: 24px;
            background: #fafafa;
            border-radius: 12px;
            border: 1px solid rgba(0,0,0,0.05);
        }
        
        .assessment-subtitle {
            color: var(--text-secondary);
            font-size: 14px;
            margin-bottom: 24px;
            font-style: italic;
        }
        
        .classification-section {
            margin-bottom: 32px;
        }
        
        .classification-badge {
            padding: 20px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 16px;
        }
        
        .classification-icon {
            font-size: 24px;
        }
        
        .classification-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 4px;
        }
        
        .classification-subtitle {
            font-size: 14px;
            opacity: 0.8;
        }
        
        .evidence-strength-bar {
            display: flex;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
        }
        
        .evidence-badge, .confidence-badge {
            padding: 6px 12px;
            border-radius: 16px;
            font-size: 12px;
            font-weight: 500;
            text-transform: uppercase;
        }
        
        .confidence-badge {
            background: #e7f3ff;
            color: #0066cc;
        }
        
        .evidence-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin: 16px 0;
        }
        
        .evidence-card {
            background: white;
            padding: 16px;
            border-radius: 8px;
            box-shadow: var(--shadow-subtle);
        }
        
        .evidence-header {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 12px;
        }
        
        .evidence-icon {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 14px;
        }
        
        .evidence-title {
            font-weight: 500;
            font-size: 14px;
        }
        
        .evidence-value {
            font-family: 'SF Mono', monospace;
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 4px;
        }
        
        .evidence-interpretation {
            font-size: 12px;
            color: var(--text-secondary);
        }
        
        .interpretation-section, .actionable-section, .quality-section {
            margin-bottom: 32px;
        }
        
        .interpretation-section h3, .actionable-section h3, .quality-section h3 {
            font-size: 16px;
            color: var(--text-primary);
            margin-bottom: 16px;
            border-bottom: 2px solid var(--accent-blue);
            padding-bottom: 8px;
        }
        
        .interpretation-content > div {
            margin-bottom: 20px;
        }
        
        .interpretation-content h4 {
            font-size: 14px;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }
        
        .gene-list {
            background: #f0f8ff;
            padding: 8px 12px;
            border-radius: 4px;
            font-family: 'SF Mono', monospace;
            font-weight: 500;
            color: var(--accent-blue);
        }
        
        .insights-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
        }
        
        .insight-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: var(--shadow-subtle);
        }
        
        .insight-card h4 {
            margin-bottom: 12px;
            font-size: 14px;
        }
        
        .experiment-list, .limitation-list {
            margin: 0;
            padding-left: 20px;
        }
        
        .experiment-list li, .limitation-list li {
            margin-bottom: 8px;
            font-size: 14px;
            line-height: 1.4;
        }
        
        .methodology-note {
            background: #e7f3ff;
            padding: 16px;
            border-radius: 8px;
            border-left: 4px solid var(--accent-blue);
            font-size: 14px;
            margin-top: 20px;
        }
        
        @media (max-width: 768px) {
            .insights-grid {
                grid-template-columns: 1fr;
            }
            
            .evidence-grid {
                grid-template-columns: 1fr;
            }
        }
        """