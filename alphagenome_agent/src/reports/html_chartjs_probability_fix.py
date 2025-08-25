def _generate_enhancer_probability_chart(self, safe_id: str, result: Dict[str, Any] = None) -> str:
    """Generate exploratory signal profile chart with appropriate context."""
    
    # Check if this is a gene-proximal region
    genomic_context = result.get('genomic_context', {}) if result else {}
    is_gene_proximal = (
        genomic_context.get('is_exon', False) or 
        genomic_context.get('is_coding', False) or
        genomic_context.get('is_promoter', False)
    )
    
    # Common explanation content
    explanation_html = f"""
        <div id="explanation-{safe_id}" class="explanation-content" style="display: none;">
            <div class="explanation-section">
                <h4>🔬 How We Analyze Chromatin Signals</h4>
                <p>This profile shows chromatin signals from the AlphaGenome model across the genomic region:</p>
                
                <div class="signal-list">
                    <div class="signal-item">
                        <span class="signal-badge positive">H3K27ac</span>
                        <span class="signal-desc">Active chromatin mark - associated with active regulatory regions</span>
                    </div>
                    <div class="signal-item">
                        <span class="signal-badge positive">H3K4me1</span>
                        <span class="signal-desc">General enhancer mark - found at both active and poised enhancers</span>
                    </div>
                    <div class="signal-item">
                        <span class="signal-badge positive">DNase</span>
                        <span class="signal-desc">Open chromatin - indicates DNA is accessible for protein binding</span>
                    </div>
                    <div class="signal-item">
                        <span class="signal-badge negative">H3K4me3</span>
                        <span class="signal-desc">Promoter mark - high levels indicate promoters</span>
                    </div>
                    <div class="signal-item">
                        <span class="signal-badge neutral">RNA</span>
                        <span class="signal-desc">Transcription signal</span>
                    </div>
                </div>
                
                <p class="method-note">
                    <strong>Data Source:</strong> AlphaGenome predictions based on large-scale epigenomic datasets.
                    For reproducibility details and specific dataset accessions, see the Data Provenance section.
                </p>
            </div>
            
            <div class="explanation-section">
                <h4>⚠️ Important Context</h4>
                <div class="limitation-box">
                    <ul>
                        <li><strong>Research Use Only:</strong> This analysis is for research purposes only.</li>
                        <li><strong>Statistical Prediction:</strong> These are computational predictions that require experimental validation.</li>
                        <li><strong>Resolution:</strong> Base-pair resolution smoothed over 5bp windows.</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
    """
    
    if is_gene_proximal:
        # Show as exploratory signal profile for gene-proximal regions
        return f"""
        <div class="signal-profile-section exploratory">
            <div class="section-header">
                <h3>📊 Exploratory Signal Profile <span class="not-evaluated-badge">Not Evaluated (Gene-Body)</span></h3>
                <p class="section-description">
                    Gene-body context signals shown for documentation purposes only. 
                    These signals reflect transcriptional activity and are <strong>not counted</strong> 
                    toward enhancer classification.
                </p>
            </div>
            <div class="signal-chart-container grayed-out">
                <canvas id="prob-chart-{safe_id}"></canvas>
            </div>
            
            <div class="signal-explanation">
                <button class="explanation-toggle" onclick="toggleExplanation('{safe_id}')">
                    ℹ️ Understanding This Profile <span class="toggle-icon">▼</span>
                </button>
                {explanation_html}
        </div>
        """
    else:
        # Show standard enhancer probability for distal regions
        return f"""
        <div class="probability-chart-section">
            <div class="section-header">
                <h3>📈 Enhancer Probability Analysis</h3>
                <p class="section-description">
                    This chart estimates the probability of enhancer activity across the genomic region 
                    by combining multiple biological signals using ensemble methods.
                </p>
            </div>
            <div class="probability-chart-container">
                <canvas id="prob-chart-{safe_id}"></canvas>
            </div>
            
            <div class="probability-explanation">
                <button class="explanation-toggle" onclick="toggleExplanation('{safe_id}')">
                    ℹ️ Understanding This Chart <span class="toggle-icon">▼</span>
                </button>
                {explanation_html}
        </div>
        """