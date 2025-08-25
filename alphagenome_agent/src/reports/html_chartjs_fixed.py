    def _generate_genomic_info_html(self, result: Dict[str, Any]) -> str:
        """Generate genomic window and data information section."""
        alphagenome_result = result.get('alphagenome_result', {})
        raw_data = alphagenome_result.get('raw', {})
        
        # Calculate genomic window size and data points
        total_base_pairs = 0
        if 'reference' in raw_data:
            ref_outputs = raw_data['reference']
            if hasattr(ref_outputs, 'dnase') and ref_outputs.dnase is not None:
                total_base_pairs = len(ref_outputs.dnase.values.flatten())
        
        # Get the genomic interval
        interval = alphagenome_result.get('genomic_interval', 'Unknown region')
        
        genomic_info_html = f"""
        <div class="genomic-info-section">
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">Genomic Window</div>
                    <div class="info-value">{interval}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Analysis Resolution</div>
                    <div class="info-value">{total_base_pairs:,} base pairs</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Data Source</div>
                    <div class="info-value">AlphaGenome predictions</div>
                </div>
            </div>
        </div>
        """
        
        return genomic_info_html