#!/usr/bin/env python3
"""
Simple Enhancer Detection Pipeline
==================================

Clean, minimal implementation that does exactly what's needed:
1. Fetch mutations for a gene
2. Test each with AlphaGenome
3. Check if signals show enhancer creation
4. Create clear visualizations
5. Generate simple report with decision
"""

import os
import sys
import json
import argparse
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent / "modules"))

from mutation_fetchers.cbioportal_fetcher import cBioPortalFetcher
from alphagenome.data import genome
from alphagenome.models import dna_client

class SimpleEnhancerPipeline:
    """
    Simple, focused enhancer detection pipeline
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = dna_client.create(api_key)
        self.mutation_fetcher = cBioPortalFetcher()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Simple decision criteria
        self.enhancer_criteria = {
            'min_dnase_increase': 0.1,      # Minimum accessibility increase
            'min_rna_increase': 0.01,       # Minimum expression increase  
            'min_h3k27ac_increase': 5.0,    # Minimum H3K27ac increase
            'min_h3k4me1_increase': 2.0     # Minimum H3K4me1 increase
        }
        
        # Tissue mappings
        self.tissues = {
            'breast': 'UBERON:0000310',
            'pancreatic': 'UBERON:0001264', 
            'colorectal': 'UBERON:0001157',
            'lung': 'UBERON:0002048'
        }
        
        # Create output directories
        Path("reports/simple").mkdir(parents=True, exist_ok=True)
        Path("visualizations/simple").mkdir(parents=True, exist_ok=True)
    
    def analyze_gene(self, gene: str, cancer_type: str, max_mutations: int = 10) -> Dict[str, Any]:
        """
        Analyze if mutations in a gene create enhancers
        """
        print(f"🧬 Simple Enhancer Analysis: {gene} in {cancer_type} cancer")
        print(f"📊 Testing up to {max_mutations} mutations")
        print("="*60)
        
        # Step 1: Get mutations
        print("1️⃣ Fetching mutations from cBioPortal...")
        mutations = self._fetch_mutations(gene, cancer_type, max_mutations)
        if not mutations:
            return {'status': 'failed', 'error': 'No mutations found'}
        
        unique_mutations = self._get_unique_mutations(mutations)
        print(f"   Found {len(mutations)} mutations ({len(unique_mutations)} unique)")
        
        # Step 2: Analyze each unique mutation
        print("2️⃣ Analyzing mutations with AlphaGenome...")
        results = []
        tissue_id = self.tissues.get(cancer_type, 'UBERON:0000479')
        
        for i, mutation in enumerate(unique_mutations[:10], 1):  # Limit to 10
            print(f"   🔬 [{i}/{min(10, len(unique_mutations))}] {mutation['variant_id']}")
            result = self._analyze_single_mutation(mutation, tissue_id)
            results.append(result)
        
        # Step 3: Make enhancer decision
        print("3️⃣ Making enhancer decision...")
        decision = self._make_enhancer_decision(results)
        
        # Step 4: Create visualizations
        print("4️⃣ Creating visualizations...")
        viz_files = self._create_visualizations(results, gene, cancer_type)
        
        # Step 5: Generate report
        print("5️⃣ Generating report...")
        report_file = self._generate_report(gene, cancer_type, results, decision, viz_files)
        
        print("="*60)
        print(f"✅ Analysis complete!")
        print(f"📊 Decision: {decision['summary']}")
        print(f"📄 Report: {report_file}")
        print(f"🎨 Visualizations: {len(viz_files)} created")
        
        return {
            'status': 'success',
            'gene': gene,
            'cancer_type': cancer_type,
            'mutations_tested': len(results),
            'decision': decision,
            'report_file': report_file,
            'visualizations': viz_files
        }
    
    def _fetch_mutations(self, gene: str, cancer_type: str, max_mutations: int) -> List[Dict[str, Any]]:
        """Fetch mutations from cBioPortal"""
        mutation_data = self.mutation_fetcher.fetch_mutations(gene, cancer_type, max_mutations)
        if mutation_data['status'] == 'success':
            return mutation_data['mutations']
        return []
    
    def _get_unique_mutations(self, mutations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get unique mutations (avoid duplicates)"""
        unique = {}
        for mut in mutations:
            key = f"{mut['chromosome']}:{mut['position']}:{mut['ref']}>{mut['alt']}"
            if key not in unique:
                unique[key] = mut
        return list(unique.values())
    
    def _analyze_single_mutation(self, mutation: Dict[str, Any], tissue_id: str) -> Dict[str, Any]:
        """Analyze single mutation with AlphaGenome"""
        try:
            # Create AlphaGenome variant
            variant = genome.Variant(
                chromosome=mutation['chromosome'],
                position=mutation['position'],
                reference_bases=mutation['ref'],
                alternate_bases=mutation['alt']
            )
            
            # Get predictions
            interval = variant.reference_interval.resize(131_072)
            outputs = self.model.predict_variant(
                interval=interval,
                variant=variant,
                requested_outputs=[
                    dna_client.OutputType.DNASE,
                    dna_client.OutputType.CHIP_HISTONE, 
                    dna_client.OutputType.RNA_SEQ
                ],
                ontology_terms=[tissue_id]
            )
            
            # Extract and analyze data
            analysis = self._extract_signal_data(outputs)
            analysis['variant_id'] = mutation.get('variant_id', 'Unknown')
            analysis['mutation'] = mutation
            analysis['status'] = 'success'
            
            return analysis
            
        except Exception as e:
            return {
                'status': 'failed',
                'variant_id': mutation.get('variant_id', 'Unknown'),
                'error': str(e)
            }
    
    def _extract_signal_data(self, outputs) -> Dict[str, Any]:
        """Extract and compare reference vs variant signals"""
        analysis = {
            'dnase': {'available': False},
            'rna': {'available': False}, 
            'histones': {'available': False}
        }
        
        # DNase accessibility
        if hasattr(outputs.reference, 'dnase') and outputs.reference.dnase is not None:
            ref_dnase = outputs.reference.dnase.values.flatten()
            alt_dnase = outputs.alternate.dnase.values.flatten()
            
            analysis['dnase'] = {
                'available': True,
                'ref_mean': float(np.mean(ref_dnase)),
                'alt_mean': float(np.mean(alt_dnase)),
                'ref_max': float(np.max(ref_dnase)),
                'alt_max': float(np.max(alt_dnase)),
                'mean_increase': float(np.mean(alt_dnase - ref_dnase)),
                'max_increase': float(np.max(alt_dnase - ref_dnase)),
                'ref_data': ref_dnase,
                'alt_data': alt_dnase
            }
        
        # RNA expression
        if hasattr(outputs.reference, 'rna_seq') and outputs.reference.rna_seq is not None:
            ref_rna = outputs.reference.rna_seq.values
            alt_rna = outputs.alternate.rna_seq.values
            
            if ref_rna.size > 0:
                analysis['rna'] = {
                    'available': True,
                    'ref_mean': float(np.mean(ref_rna)),
                    'alt_mean': float(np.mean(alt_rna)),
                    'mean_increase': float(np.mean(alt_rna - ref_rna)),
                    'max_increase': float(np.max(alt_rna - ref_rna)),
                    'ref_data': ref_rna,
                    'alt_data': alt_rna
                }
        
        # Histone modifications
        if hasattr(outputs.reference, 'chip_histone') and outputs.reference.chip_histone is not None:
            ref_hist = outputs.reference.chip_histone.values
            alt_hist = outputs.alternate.chip_histone.values
            metadata = outputs.reference.chip_histone.metadata
            
            if ref_hist.size > 0:
                histone_names = metadata.get('name', []).tolist() if 'name' in metadata else []
                analysis['histones'] = {
                    'available': True,
                    'marks': {},
                    'ref_data': ref_hist,
                    'alt_data': alt_hist,
                    'mark_names': histone_names
                }
                
                # Analyze each histone mark
                for i, mark_name in enumerate(histone_names):
                    if i < ref_hist.shape[1]:
                        ref_signal = ref_hist[:, i]
                        alt_signal = alt_hist[:, i]
                        
                        analysis['histones']['marks'][mark_name] = {
                            'ref_mean': float(np.mean(ref_signal)),
                            'alt_mean': float(np.mean(alt_signal)),
                            'mean_increase': float(np.mean(alt_signal - ref_signal)),
                            'max_increase': float(np.max(alt_signal - ref_signal))
                        }
        
        return analysis
    
    def _make_enhancer_decision(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Make simple enhancer decision based on clear criteria"""
        enhancer_evidence = []
        successful_results = [r for r in results if r.get('status') == 'success']
        
        for result in successful_results:
            variant_id = result.get('variant_id', 'Unknown')
            evidence = {'variant': variant_id, 'enhancer_signals': []}
            
            # Check DNase accessibility
            if result['dnase']['available']:
                max_increase = result['dnase']['max_increase']
                if max_increase >= self.enhancer_criteria['min_dnase_increase']:
                    evidence['enhancer_signals'].append(f"DNase increase: {max_increase:.3f}")
            
            # Check RNA expression
            if result['rna']['available']:
                max_increase = result['rna']['max_increase']
                if max_increase >= self.enhancer_criteria['min_rna_increase']:
                    evidence['enhancer_signals'].append(f"RNA increase: {max_increase:.6f}")
            
            # Check H3K27ac (active enhancer mark)
            if result['histones']['available']:
                for mark_name, mark_data in result['histones']['marks'].items():
                    if 'H3K27ac' in mark_name:
                        max_increase = mark_data['max_increase']
                        if max_increase >= self.enhancer_criteria['min_h3k27ac_increase']:
                            evidence['enhancer_signals'].append(f"H3K27ac increase: {max_increase:.1f}")
                    
                    if 'H3K4me1' in mark_name:
                        max_increase = mark_data['max_increase']
                        if max_increase >= self.enhancer_criteria['min_h3k4me1_increase']:
                            evidence['enhancer_signals'].append(f"H3K4me1 increase: {max_increase:.1f}")
            
            if evidence['enhancer_signals']:
                enhancer_evidence.append(evidence)
        
        # Make final decision
        total_mutations = len(successful_results)
        enhancer_mutations = len(enhancer_evidence)
        
        if enhancer_mutations == 0:
            decision = "NO - No enhancer signals detected"
        elif enhancer_mutations == total_mutations:
            decision = f"YES - All {total_mutations} mutations show enhancer signals"
        else:
            decision = f"PARTIAL - {enhancer_mutations}/{total_mutations} mutations show enhancer signals"
        
        return {
            'summary': decision,
            'total_mutations': total_mutations,
            'enhancer_mutations': enhancer_mutations,
            'evidence': enhancer_evidence,
            'criteria_used': self.enhancer_criteria
        }
    
    def _create_visualizations(self, results: List[Dict[str, Any]], gene: str, cancer_type: str) -> List[str]:
        """Create simple, clear visualizations"""
        viz_files = []
        successful_results = [r for r in results if r.get('status') == 'success']
        
        if not successful_results:
            return viz_files
        
        # 1. Signal comparison plot for each mutation
        for i, result in enumerate(successful_results):
            viz_file = self._plot_mutation_signals(result, gene, cancer_type, i)
            if viz_file:
                viz_files.append(viz_file)
        
        # 2. Summary comparison plot
        viz_file = self._plot_summary_comparison(successful_results, gene, cancer_type)
        if viz_file:
            viz_files.append(viz_file)
        
        return viz_files
    
    def _plot_mutation_signals(self, result: Dict[str, Any], gene: str, cancer_type: str, index: int) -> Optional[str]:
        """Plot reference vs variant signals for one mutation"""
        variant_id = result.get('variant_id', f'mutation_{index+1}')
        
        # Count available signals
        available_signals = sum([
            result['dnase']['available'],
            result['rna']['available'], 
            result['histones']['available']
        ])
        
        if available_signals == 0:
            return None
        
        fig, axes = plt.subplots(1, available_signals, figsize=(5*available_signals, 5))
        if available_signals == 1:
            axes = [axes]
        
        plot_idx = 0
        
        # DNase plot
        if result['dnase']['available']:
            ax = axes[plot_idx]
            ref_data = result['dnase']['ref_data'][:1000]  # First 1000 points for clarity
            alt_data = result['dnase']['alt_data'][:1000]
            
            x = range(len(ref_data))
            ax.plot(x, ref_data, 'b-', alpha=0.7, label='Reference')
            ax.plot(x, alt_data, 'r-', alpha=0.7, label='Variant')
            ax.set_title(f'DNase Accessibility\nMax increase: {result["dnase"]["max_increase"]:.3f}')
            ax.set_ylabel('Accessibility')
            ax.legend()
            ax.grid(True, alpha=0.3)
            plot_idx += 1
        
        # RNA plot
        if result['rna']['available']:
            ax = axes[plot_idx] 
            ref_data = result['rna']['ref_data'].flatten()[:1000]
            alt_data = result['rna']['alt_data'].flatten()[:1000]
            
            x = range(len(ref_data))
            ax.plot(x, ref_data, 'b-', alpha=0.7, label='Reference')
            ax.plot(x, alt_data, 'r-', alpha=0.7, label='Variant')
            ax.set_title(f'RNA Expression\nMax increase: {result["rna"]["max_increase"]:.6f}')
            ax.set_ylabel('Expression')
            ax.legend()
            ax.grid(True, alpha=0.3)
            plot_idx += 1
        
        # Histone plot
        if result['histones']['available']:
            ax = axes[plot_idx]
            mark_names = result['histones']['mark_names'][:3]  # Show top 3 marks
            
            ref_means = []
            alt_means = []
            labels = []
            
            for mark_name in mark_names:
                if mark_name in result['histones']['marks']:
                    mark_data = result['histones']['marks'][mark_name]
                    ref_means.append(mark_data['ref_mean'])
                    alt_means.append(mark_data['alt_mean'])
                    labels.append(mark_name.split()[-1])  # Just the mark name
            
            if ref_means:
                x = range(len(labels))
                width = 0.35
                ax.bar([i - width/2 for i in x], ref_means, width, label='Reference', alpha=0.7, color='blue')
                ax.bar([i + width/2 for i in x], alt_means, width, label='Variant', alpha=0.7, color='red')
                ax.set_title('Histone Modifications')
                ax.set_ylabel('Signal Level')
                ax.set_xticks(x)
                ax.set_xticklabels(labels, rotation=45)
                ax.legend()
                ax.grid(True, alpha=0.3, axis='y')
        
        plt.suptitle(f'{variant_id} - AlphaGenome Signal Comparison', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        filename = f"visualizations/simple/{gene}_{cancer_type}_{variant_id.replace('>', '_')}_{self.timestamp}.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def _plot_summary_comparison(self, results: List[Dict[str, Any]], gene: str, cancer_type: str) -> Optional[str]:
        """Create summary plot comparing all mutations"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        
        variants = []
        dnase_increases = []
        rna_increases = []
        h3k27ac_increases = []
        
        for result in results:
            variants.append(result.get('variant_id', 'Unknown').replace(f'{gene}_', ''))
            
            # DNase increases
            if result['dnase']['available']:
                dnase_increases.append(result['dnase']['max_increase'])
            else:
                dnase_increases.append(0)
            
            # RNA increases
            if result['rna']['available']:
                rna_increases.append(result['rna']['max_increase'])
            else:
                rna_increases.append(0)
            
            # H3K27ac increases
            h3k27ac_increase = 0
            if result['histones']['available']:
                for mark_name, mark_data in result['histones']['marks'].items():
                    if 'H3K27ac' in mark_name:
                        h3k27ac_increase = mark_data['max_increase']
                        break
            h3k27ac_increases.append(h3k27ac_increase)
        
        # Plot 1: DNase accessibility increases
        colors = ['red' if x >= self.enhancer_criteria['min_dnase_increase'] else 'gray' for x in dnase_increases]
        ax1.bar(range(len(variants)), dnase_increases, color=colors, alpha=0.7)
        ax1.axhline(y=self.enhancer_criteria['min_dnase_increase'], color='red', linestyle='--', alpha=0.5)
        ax1.set_title('DNase Accessibility Increases')
        ax1.set_ylabel('Max Increase')
        ax1.set_xticks(range(len(variants)))
        ax1.set_xticklabels(variants, rotation=45, ha='right')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Plot 2: RNA expression increases  
        colors = ['red' if x >= self.enhancer_criteria['min_rna_increase'] else 'gray' for x in rna_increases]
        ax2.bar(range(len(variants)), rna_increases, color=colors, alpha=0.7)
        ax2.axhline(y=self.enhancer_criteria['min_rna_increase'], color='red', linestyle='--', alpha=0.5)
        ax2.set_title('RNA Expression Increases')
        ax2.set_ylabel('Max Increase')
        ax2.set_xticks(range(len(variants)))
        ax2.set_xticklabels(variants, rotation=45, ha='right')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Plot 3: H3K27ac increases
        colors = ['red' if x >= self.enhancer_criteria['min_h3k27ac_increase'] else 'gray' for x in h3k27ac_increases]
        ax3.bar(range(len(variants)), h3k27ac_increases, color=colors, alpha=0.7)
        ax3.axhline(y=self.enhancer_criteria['min_h3k27ac_increase'], color='red', linestyle='--', alpha=0.5)
        ax3.set_title('H3K27ac Increases (Active Enhancer Mark)')
        ax3.set_ylabel('Max Increase')
        ax3.set_xticks(range(len(variants)))
        ax3.set_xticklabels(variants, rotation=45, ha='right')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # Plot 4: Summary decision
        enhancer_counts = []
        for i in range(len(variants)):
            count = 0
            if dnase_increases[i] >= self.enhancer_criteria['min_dnase_increase']:
                count += 1
            if rna_increases[i] >= self.enhancer_criteria['min_rna_increase']:
                count += 1  
            if h3k27ac_increases[i] >= self.enhancer_criteria['min_h3k27ac_increase']:
                count += 1
            enhancer_counts.append(count)
        
        colors = ['green' if x >= 2 else 'orange' if x == 1 else 'gray' for x in enhancer_counts]
        ax4.bar(range(len(variants)), enhancer_counts, color=colors, alpha=0.7)
        ax4.set_title('Enhancer Evidence Count\n(Green=Strong, Orange=Weak)')
        ax4.set_ylabel('Number of Enhancer Signals')
        ax4.set_xticks(range(len(variants)))
        ax4.set_xticklabels(variants, rotation=45, ha='right')
        ax4.set_ylim(0, 3)
        ax4.grid(True, alpha=0.3, axis='y')
        
        plt.suptitle(f'{gene} Mutations in {cancer_type.title()} Cancer - Enhancer Analysis', 
                     fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        filename = f"visualizations/simple/{gene}_{cancer_type}_summary_{self.timestamp}.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def _generate_report(self, gene: str, cancer_type: str, results: List[Dict[str, Any]], 
                        decision: Dict[str, Any], viz_files: List[str]) -> str:
        """Generate simple, clear report"""
        successful_results = [r for r in results if r.get('status') == 'success']
        
        report = f"""# Simple Enhancer Analysis: {gene} in {cancer_type.title()} Cancer

**Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Question**: Do {gene} mutations create new enhancers?

## Decision: {decision['summary']}

### Analysis Summary
- **Total Mutations Tested**: {decision['total_mutations']}
- **Mutations with Enhancer Signals**: {decision['enhancer_mutations']}
- **Success Rate**: {decision['enhancer_mutations']}/{decision['total_mutations']} ({100*decision['enhancer_mutations']/max(1,decision['total_mutations']):.0f}%)

### Detection Criteria Used
- **DNase Accessibility Increase**: ≥ {decision['criteria_used']['min_dnase_increase']}
- **RNA Expression Increase**: ≥ {decision['criteria_used']['min_rna_increase']}  
- **H3K27ac Increase**: ≥ {decision['criteria_used']['min_h3k27ac_increase']}
- **H3K4me1 Increase**: ≥ {decision['criteria_used']['min_h3k4me1_increase']}

## Results by Mutation

"""
        
        for result in successful_results:
            variant_id = result.get('variant_id', 'Unknown')
            report += f"### {variant_id}\n\n"
            
            # Data availability
            report += "**Data Available**: "
            available = []
            if result['dnase']['available']:
                available.append("DNase")
            if result['rna']['available']:
                available.append("RNA")
            if result['histones']['available']:
                available.append("Histones")
            report += ", ".join(available) if available else "None"
            report += "\n\n"
            
            # Signal changes
            if result['dnase']['available']:
                increase = result['dnase']['max_increase']
                status = "✅ ENHANCER SIGNAL" if increase >= decision['criteria_used']['min_dnase_increase'] else "❌ No signal"
                report += f"**DNase Accessibility**: Max increase = {increase:.3f} ({status})\n"
            
            if result['rna']['available']:
                increase = result['rna']['max_increase']
                status = "✅ ENHANCER SIGNAL" if increase >= decision['criteria_used']['min_rna_increase'] else "❌ No signal"
                report += f"**RNA Expression**: Max increase = {increase:.6f} ({status})\n"
            
            if result['histones']['available']:
                for mark_name, mark_data in result['histones']['marks'].items():
                    if 'H3K27ac' in mark_name or 'H3K4me1' in mark_name:
                        increase = mark_data['max_increase']
                        threshold = decision['criteria_used']['min_h3k27ac_increase'] if 'H3K27ac' in mark_name else decision['criteria_used']['min_h3k4me1_increase']
                        status = "✅ ENHANCER SIGNAL" if increase >= threshold else "❌ No signal"
                        report += f"**{mark_name}**: Max increase = {increase:.1f} ({status})\n"
            
            report += "\n"
        
        # Add visualizations
        if viz_files:
            report += "## Visualizations\n\n"
            for viz_file in viz_files:
                filename = Path(viz_file).name
                if 'summary' in filename:
                    report += f"**Summary Comparison**: ![Summary]({viz_file})\n\n"
                else:
                    mutation_name = filename.split('_')[2:4]  # Extract mutation identifier
                    report += f"**{'_'.join(mutation_name)} Signals**: ![Signals]({viz_file})\n\n"
        
        report += f"""## Methodology

This analysis uses AlphaGenome to predict the regulatory effects of mutations:

1. **Mutation Collection**: Real mutations from cBioPortal database
2. **AlphaGenome Prediction**: Reference vs variant genome predictions for:
   - DNase-seq (chromatin accessibility)
   - RNA-seq (gene expression)
   - ChIP-seq (histone modifications)
3. **Enhancer Detection**: Look for increases in accessibility and active marks
4. **Decision Making**: Apply quantitative thresholds to determine enhancer creation

### Interpretation
- **DNase increases**: Indicate new accessible chromatin regions
- **H3K27ac increases**: Mark active enhancers
- **H3K4me1 increases**: Mark enhancer priming
- **RNA increases**: Show downstream transcriptional effects

Strong enhancer evidence requires multiple signals above thresholds.
"""
        
        # Save report
        report_file = f"reports/simple/{gene}_{cancer_type}_simple_analysis_{self.timestamp}.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        return report_file


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Simple Enhancer Detection Pipeline")
    parser.add_argument('--gene', required=True, help='Gene to analyze (e.g., KRAS, TP53)')
    parser.add_argument('--cancer', required=True, choices=['breast', 'pancreatic', 'colorectal', 'lung'],
                       help='Cancer type')
    parser.add_argument('--max-mutations', type=int, default=10, help='Max mutations to test')
    
    args = parser.parse_args()
    
    # Get API key
    api_key = os.environ.get('ALPHAGENOME_API_KEY')
    if not api_key:
        print("❌ ERROR: Set ALPHAGENOME_API_KEY environment variable")
        return 1
    
    # Run analysis
    pipeline = SimpleEnhancerPipeline(api_key)
    result = pipeline.analyze_gene(args.gene, args.cancer, args.max_mutations)
    
    if result['status'] == 'success':
        print(f"\n🎉 Success! Check {result['report_file']}")
        return 0
    else:
        print(f"\n❌ Failed: {result.get('error')}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())