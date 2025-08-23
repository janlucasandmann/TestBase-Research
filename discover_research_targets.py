#!/usr/bin/env python3
"""
Discover Research Targets: Find genes with rich variant data in cBioPortal
This script helps identify the best research questions based on actual data availability
"""

import requests
import pandas as pd
import json
from typing import Dict, List, Tuple
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns

class ResearchTargetDiscovery:
    """
    Discover genes with rich mutation data for research questions
    """
    
    def __init__(self):
        self.base_url = "https://www.cbioportal.org/api"
        self.cancer_studies = {
            'glioblastoma': ['gbm_tcga_pan_can_atlas_2018', 'lgg_tcga_pan_can_atlas_2018'],
            'lung': ['luad_tcga_pan_can_atlas_2018', 'lusc_tcga_pan_can_atlas_2018'],
            'breast': ['brca_tcga_pan_can_atlas_2018'],
            'colorectal': ['coadread_tcga_pan_can_atlas_2018'],
            'pancreatic': ['paad_tcga_pan_can_atlas_2018'],
            'melanoma': ['skcm_tcga_pan_can_atlas_2018'],
            'prostate': ['prad_tcga_pan_can_atlas_2018'],
            'ovarian': ['ov_tcga_pan_can_atlas_2018'],
        }
        
    def get_top_mutated_genes(self, study_id: str, profile_id: str, top_n: int = 50) -> List[Dict]:
        """
        Get the most frequently mutated genes in a study
        """
        try:
            # First get sample list
            sample_list_id = f"{study_id}_all"
            
            # Use the mutated genes endpoint for better performance
            url = f"{self.base_url}/molecular-profiles/{profile_id}/mutated-genes"
            params = {
                'sampleListId': sample_list_id
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                mutated_genes = response.json()
                
                # Extract gene mutation frequencies
                top_genes = []
                for gene_data in mutated_genes[:top_n]:
                    gene_symbol = gene_data.get('hugoGeneSymbol', 'Unknown')
                    entrez_id = gene_data.get('entrezGeneId', 0)
                    mutation_count = gene_data.get('countByEntity', 0)
                    
                    if gene_symbol != 'Unknown' and mutation_count > 0:
                        top_genes.append({
                            'gene': gene_symbol,
                            'mutation_count': mutation_count,
                            'entrezId': entrez_id,
                            'frequency': gene_data.get('frequency', 0),
                            'qValue': gene_data.get('qValue', 1.0)
                        })
                
                return top_genes
            
            return []
            
        except Exception as e:
            print(f"Error fetching mutations for {study_id}: {e}")
            return []
    
    def analyze_cancer_type(self, cancer_type: str) -> Dict:
        """
        Analyze all studies for a cancer type to find highly mutated genes
        """
        print(f"\n{'='*60}")
        print(f"Analyzing {cancer_type.upper()}")
        print(f"{'='*60}")
        
        if cancer_type not in self.cancer_studies:
            print(f"Unknown cancer type: {cancer_type}")
            return {}
        
        all_gene_counts = Counter()
        study_results = []
        
        for study_id in self.cancer_studies[cancer_type]:
            print(f"\n📊 Checking {study_id}...")
            profile_id = f"{study_id}_mutations"
            
            top_genes = self.get_top_mutated_genes(study_id, profile_id, top_n=30)
            
            if top_genes:
                print(f"  ✅ Found {len(top_genes)} highly mutated genes")
                
                # Add to overall counts
                for gene_data in top_genes:
                    all_gene_counts[gene_data['gene']] += gene_data['mutation_count']
                
                study_results.append({
                    'study': study_id,
                    'top_genes': top_genes[:10]  # Keep top 10 for each study
                })
            else:
                print(f"  ⚠️ No data available")
        
        # Get overall top genes for this cancer type
        top_genes_overall = []
        for gene, total_count in all_gene_counts.most_common(20):
            top_genes_overall.append({
                'gene': gene,
                'total_mutations': total_count,
                'studies': len([s for s in study_results if any(g['gene'] == gene for g in s['top_genes'])])
            })
        
        return {
            'cancer_type': cancer_type,
            'top_genes': top_genes_overall,
            'study_details': study_results
        }
    
    def discover_all_targets(self) -> Dict:
        """
        Discover research targets across all cancer types
        """
        print("🔬 DISCOVERING RESEARCH TARGETS ACROSS CANCER TYPES")
        print("=" * 60)
        
        all_results = {}
        
        for cancer_type in self.cancer_studies.keys():
            results = self.analyze_cancer_type(cancer_type)
            if results:
                all_results[cancer_type] = results
        
        return all_results
    
    def generate_research_questions(self, discovery_results: Dict) -> List[Dict]:
        """
        Generate research questions based on discovered targets
        """
        research_questions = []
        
        # Define question templates
        templates = [
            "How do {gene} mutations create de novo enhancers in {cancer}?",
            "What tissue-specific regulatory elements are disrupted by {gene} variants in {cancer}?",
            "How do {gene} mutations affect long-range chromatin interactions in {cancer}?",
            "Which {gene} variants alter splicing patterns in {cancer}?",
            "How do non-coding {gene} variants influence expression in {cancer}?",
            "What convergent regulatory mechanisms are shared by {gene} mutations in {cancer}?",
        ]
        
        # Generate questions for top genes in each cancer
        for cancer_type, results in discovery_results.items():
            for gene_data in results['top_genes'][:5]:  # Top 5 genes per cancer
                gene = gene_data['gene']
                mutations = gene_data['total_mutations']
                
                # Select appropriate template based on mutation count
                if mutations > 100:
                    template_idx = [0, 1, 2]  # Complex questions for highly mutated genes
                elif mutations > 50:
                    template_idx = [1, 3, 4]  # Medium complexity
                else:
                    template_idx = [4, 5]  # Simpler questions
                
                for idx in template_idx[:2]:  # Generate 2 questions per gene
                    question = {
                        'question': templates[idx].format(gene=gene, cancer=cancer_type),
                        'gene': gene,
                        'cancer_type': cancer_type,
                        'data_availability': mutations,
                        'priority': 'HIGH' if mutations > 100 else 'MEDIUM' if mutations > 50 else 'LOW'
                    }
                    research_questions.append(question)
        
        # Sort by data availability
        research_questions.sort(key=lambda x: x['data_availability'], reverse=True)
        
        return research_questions
    
    def create_visualization(self, discovery_results: Dict):
        """
        Create visualization of mutation frequencies across cancers
        """
        # Prepare data for heatmap
        genes_set = set()
        for cancer_type, results in discovery_results.items():
            for gene_data in results['top_genes'][:10]:
                genes_set.add(gene_data['gene'])
        
        genes_list = sorted(list(genes_set))
        cancer_types = list(discovery_results.keys())
        
        # Create matrix
        matrix = []
        for cancer in cancer_types:
            row = []
            gene_counts = {g['gene']: g['total_mutations'] 
                          for g in discovery_results[cancer]['top_genes']}
            for gene in genes_list:
                row.append(gene_counts.get(gene, 0))
            matrix.append(row)
        
        # Create heatmap
        plt.figure(figsize=(20, 10))
        sns.heatmap(matrix, 
                    xticklabels=genes_list,
                    yticklabels=cancer_types,
                    cmap='YlOrRd',
                    annot=True,
                    fmt='d',
                    cbar_kws={'label': 'Mutation Count'})
        
        plt.title('Gene Mutation Frequencies Across Cancer Types\n(Data from cBioPortal)', 
                  fontsize=16, fontweight='bold')
        plt.xlabel('Genes', fontsize=12)
        plt.ylabel('Cancer Types', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Save figure
        plt.savefig('research_targets_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("\n📊 Heatmap saved as 'research_targets_heatmap.png'")
    
    def save_results(self, discovery_results: Dict, research_questions: List[Dict]):
        """
        Save results to files
        """
        # Save raw discovery data
        with open('discovered_targets.json', 'w') as f:
            json.dump(discovery_results, f, indent=2, default=str)
        
        # Save research questions as markdown
        with open('recommended_research_questions.md', 'w') as f:
            f.write("# Recommended Research Questions Based on Data Availability\n\n")
            f.write("Generated from cBioPortal mutation data analysis\n\n")
            
            # Group by priority
            high_priority = [q for q in research_questions if q['priority'] == 'HIGH']
            medium_priority = [q for q in research_questions if q['priority'] == 'MEDIUM']
            low_priority = [q for q in research_questions if q['priority'] == 'LOW']
            
            f.write("## 🔴 HIGH PRIORITY (>100 mutations available)\n\n")
            for i, q in enumerate(high_priority[:10], 1):
                f.write(f"{i}. **{q['question']}**\n")
                f.write(f"   - Gene: {q['gene']}\n")
                f.write(f"   - Cancer: {q['cancer_type']}\n")
                f.write(f"   - Available mutations: {q['data_availability']}\n\n")
            
            f.write("\n## 🟡 MEDIUM PRIORITY (50-100 mutations available)\n\n")
            for i, q in enumerate(medium_priority[:10], 1):
                f.write(f"{i}. **{q['question']}**\n")
                f.write(f"   - Gene: {q['gene']}\n")
                f.write(f"   - Cancer: {q['cancer_type']}\n")
                f.write(f"   - Available mutations: {q['data_availability']}\n\n")
            
            f.write("\n## 🟢 LOW PRIORITY (<50 mutations available)\n\n")
            for i, q in enumerate(low_priority[:5], 1):
                f.write(f"{i}. **{q['question']}**\n")
                f.write(f"   - Gene: {q['gene']}\n")
                f.write(f"   - Cancer: {q['cancer_type']}\n")
                f.write(f"   - Available mutations: {q['data_availability']}\n\n")
        
        # Save summary statistics
        with open('discovery_summary.txt', 'w') as f:
            f.write("RESEARCH TARGET DISCOVERY SUMMARY\n")
            f.write("="*50 + "\n\n")
            
            total_mutations = 0
            for cancer_type, results in discovery_results.items():
                cancer_total = sum(g['total_mutations'] for g in results['top_genes'])
                total_mutations += cancer_total
                f.write(f"{cancer_type.upper()}:\n")
                f.write(f"  Top 3 genes: {', '.join(g['gene'] for g in results['top_genes'][:3])}\n")
                f.write(f"  Total mutations in top 20 genes: {cancer_total}\n\n")
            
            f.write(f"\nTOTAL MUTATIONS DISCOVERED: {total_mutations}\n")
            f.write(f"RESEARCH QUESTIONS GENERATED: {len(research_questions)}\n")
        
        print("\n📁 Results saved:")
        print("  - discovered_targets.json (raw data)")
        print("  - recommended_research_questions.md (prioritized questions)")
        print("  - discovery_summary.txt (statistics)")


def main():
    """
    Main discovery workflow
    """
    print("🚀 Starting Research Target Discovery...")
    print("This will query cBioPortal to find genes with rich mutation data\n")
    
    discoverer = ResearchTargetDiscovery()
    
    # Discover targets across all cancer types
    discovery_results = discoverer.discover_all_targets()
    
    # Generate research questions
    print("\n\n📝 Generating research questions based on data availability...")
    research_questions = discoverer.generate_research_questions(discovery_results)
    
    # Create visualization
    print("\n📊 Creating visualization...")
    discoverer.create_visualization(discovery_results)
    
    # Save results
    print("\n💾 Saving results...")
    discoverer.save_results(discovery_results, research_questions)
    
    # Print summary
    print("\n" + "="*60)
    print("✅ DISCOVERY COMPLETE!")
    print("="*60)
    
    print(f"\nTop 5 recommended research questions:")
    for i, q in enumerate(research_questions[:5], 1):
        print(f"\n{i}. {q['question']}")
        print(f"   📊 Data: {q['data_availability']} mutations available")
    
    print("\n📚 Check 'recommended_research_questions.md' for full list")
    print("📊 Check 'research_targets_heatmap.png' for visualization")
    
    return discovery_results, research_questions


if __name__ == "__main__":
    results, questions = main()