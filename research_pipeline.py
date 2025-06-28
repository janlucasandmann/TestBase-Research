#!/usr/bin/env python3
"""
Automated pipeline for cancer research questions using cBioPortal + AlphaGenome
This can be called by an AI agent to answer specific research questions
"""

import requests
import pandas as pd
import json
from typing import Dict, List, Optional
from alphagenome.data import genome
from alphagenome.models import dna_client
import matplotlib.pyplot as plt
import numpy as np

class CancerResearchPipeline:
    """
    Complete pipeline from question to answer using cBioPortal and AlphaGenome
    """
    
    def __init__(self, alphagenome_api_key: str):
        self.alphagenome_key = alphagenome_api_key
        self.alphagenome_model = None
        self.cbioportal_base = "https://www.cbioportal.org/api"
        
    def process_research_question(self, question: str, gene: str, cancer_type: Optional[str] = None) -> Dict:
        """
        Main entry point: takes a research question and returns a complete analysis
        
        Args:
            question: Research question (e.g., "How does BRAF V600E affect melanoma drug resistance?")
            gene: Gene of interest (e.g., "BRAF", "EGFR", "KRAS")
            cancer_type: Optional cancer type filter (e.g., "melanoma", "lung", "colorectal")
            
        Returns:
            Dict with complete analysis results and report
        """
        
        print(f"=== Processing Research Question ===")
        print(f"Question: {question}")
        print(f"Gene: {gene}")
        print(f"Cancer type: {cancer_type or 'All'}\n")
        
        # Step 1: Pull data from cBioPortal
        print("Step 1: Fetching mutation data from cBioPortal...")
        mutations_df = self.fetch_gene_mutations(gene, cancer_type)
        
        if mutations_df.empty:
            return {
                "status": "error",
                "message": f"No mutations found for {gene}",
                "report": f"Unable to find mutation data for {gene} in cBioPortal"
            }
        
        print(f"  Found {len(mutations_df)} mutations")
        
        # Step 2: Prepare data for AlphaGenome
        print("\nStep 2: Preparing data for AlphaGenome...")
        alphagenome_data = self.prepare_for_alphagenome(mutations_df, gene)
        print(f"  Prepared {len(alphagenome_data['variants'])} variants for analysis")
        
        # Step 3: Run AlphaGenome analysis
        print("\nStep 3: Running AlphaGenome analysis...")
        analysis_results = self.run_alphagenome_analysis(alphagenome_data, gene)
        
        # Step 4: Generate report
        print("\nStep 4: Generating report...")
        report = self.generate_report(question, gene, mutations_df, analysis_results)
        
        # Step 5: Create visualizations
        print("\nStep 5: Creating visualizations...")
        visualizations = self.create_visualizations(gene, mutations_df, analysis_results)
        
        return {
            "status": "success",
            "question": question,
            "gene": gene,
            "cancer_type": cancer_type,
            "total_mutations": len(mutations_df),
            "analysis_results": analysis_results,
            "report": report,
            "visualizations": visualizations,
            "raw_data": {
                "mutations": mutations_df.to_dict(),
                "alphagenome_results": analysis_results
            }
        }
    
    def fetch_gene_mutations(self, gene: str, cancer_type: Optional[str] = None) -> pd.DataFrame:
        """Fetch mutations for a specific gene from cBioPortal"""
        
        # Get gene ID
        gene_response = requests.get(f"{self.cbioportal_base}/genes/{gene}")
        if gene_response.status_code != 200:
            return pd.DataFrame()
        
        gene_info = gene_response.json()
        entrez_id = gene_info.get('entrezGeneId')
        
        # Find appropriate studies
        if cancer_type:
            # Map cancer type to study IDs
            cancer_study_map = {
                'lung': ['msk_impact_2017', 'nsclc_tcga_broad_2016', 'luad_tcga'],
                'melanoma': ['mel_msk_impact_2020', 'skcm_tcga'],
                'colorectal': ['crc_msk_2017', 'coadread_tcga'],
                'breast': ['brca_tcga', 'breast_msk_impact_2021'],
                'pancreatic': ['paad_tcga', 'pancreas_msk_impact_2020']
            }
            
            study_ids = cancer_study_map.get(cancer_type.lower(), ['msk_impact_2017'])
        else:
            # Use comprehensive studies
            study_ids = ['msk_impact_2017', 'tcga_pan_can_atlas_2018']
        
        all_mutations = []
        
        for study_id in study_ids:
            try:
                # Try to get mutations
                url = f"{self.cbioportal_base}/molecular-profiles/{study_id}_mutations/mutations"
                params = {
                    'sampleListId': f'{study_id}_all',
                    'entrezGeneId': entrez_id,
                    'projection': 'DETAILED'
                }
                
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    mutations = response.json()
                    for mut in mutations:
                        mut['study_id'] = study_id
                    all_mutations.extend(mutations)
            except:
                continue
        
        return pd.DataFrame(all_mutations)
    
    def prepare_for_alphagenome(self, mutations_df: pd.DataFrame, gene: str) -> Dict:
        """Prepare mutation data for AlphaGenome analysis"""
        
        # Get unique variants
        unique_variants = mutations_df.drop_duplicates(
            subset=['chr', 'startPosition', 'referenceAllele', 'variantAllele']
        )
        
        # Get gene coordinates (you might need to look these up)
        gene_coords = self.get_gene_coordinates(gene)
        
        prepared_data = {
            'gene': gene,
            'gene_coordinates': gene_coords,
            'variants': [],
            'mutation_types': {}
        }
        
        # Categorize mutations
        for _, mut in unique_variants.iterrows():
            # Get chromosome and ensure it has 'chr' prefix
            chr_value = str(mut.get('chr', ''))
            if chr_value and not chr_value.startswith('chr'):
                chr_value = 'chr' + chr_value
            
            # Get reference and alternate alleles
            ref_allele = mut.get('referenceAllele', '')
            alt_allele = mut.get('variantAllele', '')
            
            # Skip deletions (AlphaGenome doesn't support '-' as alternate allele)
            if alt_allele == '-' or ref_allele == '-':
                print(f"  Skipping deletion variant at position {mut.get('startPosition', 'unknown')}")
                continue
            
            # Skip if missing required data
            if not chr_value or not ref_allele or not alt_allele:
                continue
            
            # Validate that alleles contain only valid nucleotides
            valid_bases = set('ATCG')
            if not all(base in valid_bases for base in ref_allele.upper()):
                print(f"  Skipping variant with invalid reference bases: {ref_allele}")
                continue
            if not all(base in valid_bases for base in alt_allele.upper()):
                print(f"  Skipping variant with invalid alternate bases: {alt_allele}")
                continue
            
            variant = {
                'chr': chr_value,
                'position': mut.get('startPosition', 0),
                'ref': ref_allele.upper(),
                'alt': alt_allele.upper(),
                'protein_change': mut.get('proteinChange', ''),
                'count': len(mutations_df[
                    (mutations_df['startPosition'] == mut['startPosition']) &
                    (mutations_df['referenceAllele'] == mut['referenceAllele']) &
                    (mutations_df['variantAllele'] == mut['variantAllele'])
                ])
            }
            prepared_data['variants'].append(variant)
            
            # Categorize
            protein_change = mut.get('proteinChange', '')
            if protein_change:
                prepared_data['mutation_types'][protein_change] = variant['count']
        
        return prepared_data
    
    def get_gene_coordinates(self, gene: str) -> Dict:
        """Get genomic coordinates for a gene"""
        
        # Common cancer genes - expand this list
        gene_coordinates = {
            'EGFR': {'chr': 'chr7', 'start': 55019017, 'end': 55211628},
            'BRAF': {'chr': 'chr7', 'start': 140719327, 'end': 140924928},
            'KRAS': {'chr': 'chr12', 'start': 25205246, 'end': 25250936},
            'TP53': {'chr': 'chr17', 'start': 7661779, 'end': 7687538},
            'PIK3CA': {'chr': 'chr3', 'start': 179148114, 'end': 179240093},
            'MET': {'chr': 'chr7', 'start': 116672196, 'end': 116798386},
            'ALK': {'chr': 'chr2', 'start': 29192774, 'end': 29921586},
            'ROS1': {'chr': 'chr6', 'start': 117288903, 'end': 117425833},
        }
        
        return gene_coordinates.get(gene, {
            'chr': 'unknown',
            'start': 0,
            'end': 0
        })
    
    def run_alphagenome_analysis(self, data: Dict, gene: str) -> Dict:
        """Run AlphaGenome analysis on prepared data"""
        
        if not self.alphagenome_model:
            self.alphagenome_model = dna_client.create(self.alphagenome_key)
        
        results = {
            'gene': gene,
            'total_variants': len(data['variants']),
            'variant_impacts': [],
            'regulatory_summary': {
                'mean_fold_change': 0,
                'variants_increasing_expression': 0,
                'variants_decreasing_expression': 0,
                'variants_neutral': 0
            },
            'skipped_variants': {
                'deletions': 0,
                'invalid_bases': 0,
                'missing_data': 0,
                'errors': 0
            }
        }
        
        # Analyze top variants
        top_variants = sorted(data['variants'], key=lambda x: x['count'], reverse=True)[:10]
        
        for variant in top_variants:
            # Skip variants with missing data
            if variant['chr'] == '' or variant['position'] == 0:
                results['skipped_variants']['missing_data'] += 1
                continue
            
            # Skip deletion variants (represented as '-' in cBioPortal)
            if variant['alt'] == '-':
                results['skipped_variants']['deletions'] += 1
                print(f"  Skipping deletion variant: {variant['protein_change']}")
                continue
            
            # Validate alternate bases
            if not all(base in 'ACGTN' for base in variant['alt']):
                results['skipped_variants']['invalid_bases'] += 1
                print(f"  Skipping variant with invalid bases: {variant['protein_change']} (alt: {variant['alt']})")
                continue
                
            try:
                # Fix chromosome format - add 'chr' prefix if missing
                chromosome = variant['chr']
                if not chromosome.startswith('chr'):
                    chromosome = f'chr{chromosome}'
                
                # Create AlphaGenome interval (131kb region)
                interval = genome.Interval(
                    chromosome=chromosome,
                    start=variant['position'] - 65536,
                    end=variant['position'] + 65536
                )
                
                # Create variant
                var = genome.Variant(
                    chromosome=chromosome,
                    position=variant['position'],
                    reference_bases=variant['ref'],
                    alternate_bases=variant['alt']
                )
                
                # Predict impact
                outputs = self.alphagenome_model.predict_variant(
                    interval=interval,
                    variant=var,
                    ontology_terms=['UBERON:0002048'],  # Tissue type
                    requested_outputs=[dna_client.OutputType.RNA_SEQ]
                )
                
                # Calculate impact
                ref_expr = outputs.reference.rna_seq.values.mean()
                alt_expr = outputs.alternate.rna_seq.values.mean()
                fold_change = alt_expr / ref_expr if ref_expr > 0 else 1
                
                results['variant_impacts'].append({
                    'variant': f"{variant['protein_change']}",
                    'position': variant['position'],
                    'fold_change': fold_change,
                    'log2_fc': np.log2(fold_change) if fold_change > 0 else 0,
                    'sample_count': variant['count']
                })
                
            except Exception as e:
                results['skipped_variants']['errors'] += 1
                print(f"  Error analyzing {variant['protein_change']}: {e}")
        
        # Summarize regulatory impact
        if results['variant_impacts']:
            fold_changes = [v['fold_change'] for v in results['variant_impacts']]
            results['regulatory_summary'] = {
                'mean_fold_change': np.mean(fold_changes),
                'variants_increasing_expression': sum(1 for fc in fold_changes if fc > 1.2),
                'variants_decreasing_expression': sum(1 for fc in fold_changes if fc < 0.8),
                'variants_neutral': sum(1 for fc in fold_changes if 0.8 <= fc <= 1.2)
            }
        
        # Print summary of skipped variants
        total_skipped = sum(results['skipped_variants'].values())
        if total_skipped > 0:
            print(f"\n  Skipped {total_skipped} variants:")
            for reason, count in results['skipped_variants'].items():
                if count > 0:
                    print(f"    - {reason}: {count}")
        
        return results
    
    def generate_report(self, question: str, gene: str, mutations_df: pd.DataFrame, 
                       analysis_results: Dict) -> str:
        """Generate a comprehensive report answering the research question"""
        
        report = f"""
# Research Report: {gene} Analysis

## Question
{question}

## Summary
- Gene analyzed: {gene}
- Total mutations found: {len(mutations_df)}
- Unique variants analyzed: {analysis_results['total_variants']}
- Studies included: {mutations_df['study_id'].nunique() if 'study_id' in mutations_df.columns else 'N/A'}

## Key Findings

### 1. Mutation Landscape
"""
        
        # Add top mutations
        if 'proteinChange' in mutations_df.columns:
            top_mutations = mutations_df['proteinChange'].value_counts().head(5)
            report += "Top 5 most frequent mutations:\n"
            for mut, count in top_mutations.items():
                report += f"- {mut}: {count} samples\n"
        
        report += f"\n### 2. Regulatory Impact Analysis (AlphaGenome)\n"
        
        if analysis_results['variant_impacts']:
            report += "\nVariants with significant regulatory impact:\n"
            for impact in sorted(analysis_results['variant_impacts'], 
                               key=lambda x: abs(x['log2_fc']), reverse=True)[:5]:
                direction = "↑" if impact['fold_change'] > 1 else "↓"
                report += f"- {impact['variant']}: {impact['fold_change']:.2f}x {direction} "
                report += f"(log2FC: {impact['log2_fc']:.2f}, n={impact['sample_count']})\n"
        
        if 'regulatory_summary' in analysis_results:
            summary = analysis_results['regulatory_summary']
            report += f"\nRegulatory Summary:\n"
            report += f"- Variants increasing expression: {summary['variants_increasing_expression']}\n"
            report += f"- Variants decreasing expression: {summary['variants_decreasing_expression']}\n"
            report += f"- Variants with neutral effect: {summary['variants_neutral']}\n"
        
        report += "\n### 3. Clinical Implications\n"
        
        # Add cancer-type specific insights
        if 'ONCOTREE_CODE' in mutations_df.columns:
            cancer_types = mutations_df['ONCOTREE_CODE'].value_counts().head(3)
            report += f"\nMost affected cancer types:\n"
            for cancer, count in cancer_types.items():
                report += f"- {cancer}: {count} samples\n"
        
        report += "\n### 4. Recommendations\n"
        report += "- Further investigation of high-impact regulatory variants\n"
        report += "- Validation of expression changes in patient samples\n"
        report += "- Consider therapeutic targeting strategies\n"
        
        return report
    
    def create_visualizations(self, gene: str, mutations_df: pd.DataFrame, 
                            analysis_results: Dict) -> List[str]:
        """Create visualizations for the analysis"""
        
        created_files = []
        
        # 1. Mutation frequency plot
        if 'proteinChange' in mutations_df.columns:
            plt.figure(figsize=(10, 6))
            top_muts = mutations_df['proteinChange'].value_counts().head(10)
            top_muts.plot(kind='bar')
            plt.title(f'{gene} Mutation Frequency')
            plt.xlabel('Mutation')
            plt.ylabel('Count')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            filename = f'{gene}_mutation_frequency.png'
            plt.savefig(filename)
            plt.close()
            created_files.append(filename)
        
        # 2. Regulatory impact plot
        if analysis_results['variant_impacts']:
            plt.figure(figsize=(10, 6))
            impacts = analysis_results['variant_impacts'][:10]
            variants = [v['variant'] for v in impacts]
            fold_changes = [v['log2_fc'] for v in impacts]
            
            colors = ['red' if fc < 0 else 'green' for fc in fold_changes]
            plt.bar(range(len(variants)), fold_changes, color=colors, alpha=0.7)
            plt.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
            plt.xlabel('Variant')
            plt.ylabel('Log2 Fold Change')
            plt.title(f'{gene} Variants: Regulatory Impact')
            plt.xticks(range(len(variants)), variants, rotation=45, ha='right')
            plt.tight_layout()
            filename = f'{gene}_regulatory_impact.png'
            plt.savefig(filename)
            plt.close()
            created_files.append(filename)
        
        return created_files

# Simplified wrapper function for AI agents
def analyze_cancer_question(question: str, gene: str, cancer_type: Optional[str] = None,
                          alphagenome_key: str = None) -> Dict:
    """
    Simple function that an AI agent can call
    
    Args:
        question: Research question
        gene: Gene name (e.g., "EGFR", "BRAF")
        cancer_type: Optional cancer type filter
        alphagenome_key: AlphaGenome API key
    
    Returns:
        Complete analysis results with report
    """
    
    if not alphagenome_key:
        return {"status": "error", "message": "AlphaGenome API key required"}
    
    pipeline = CancerResearchPipeline(alphagenome_key)
    return pipeline.process_research_question(question, gene, cancer_type)

# Example usage
if __name__ == "__main__":
    # Example questions an AI agent might ask
    example_questions = [
        ("How does EGFR T790M affect drug resistance in lung cancer?", "EGFR", "lung"),
        #("What is the regulatory impact of BRAF V600E in melanoma?", "BRAF", "melanoma"),
        #("How do KRAS mutations affect gene expression?", "KRAS", None),
    ]
    
    # Set your API key
    API_KEY = "AIzaSyBAs3VtzIuciUkbP7EITRyvBHbSuBVmKaA"
    
    # Process first example
    question, gene, cancer = example_questions[0]
    results = analyze_cancer_question(question, gene, cancer, API_KEY)
    
    if results['status'] == 'success':
        print(results['report'])
        print(f"\nCreated visualizations: {results['visualizations']}")
    else:
        print(f"Error: {results['message']}")