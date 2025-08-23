#!/usr/bin/env python3
"""
Simple Gene Discovery: Find frequently mutated genes using basic cBioPortal API calls
"""

import requests
import pandas as pd
from collections import Counter

def get_mutations_for_study(study_id: str, genes_list: list) -> dict:
    """
    Get mutations for a list of common cancer genes in a study
    """
    base_url = "https://www.cbioportal.org/api"
    
    print(f"\n📊 Analyzing {study_id}...")
    
    # Common cancer genes to check
    results = {}
    
    for gene in genes_list:
        try:
            # Get gene info
            gene_response = requests.get(f"{base_url}/genes/{gene}")
            if gene_response.status_code != 200:
                continue
                
            gene_info = gene_response.json()
            entrez_id = gene_info['entrezGeneId']
            
            # Get mutations for this gene
            profile_id = f"{study_id}_mutations"
            sample_list_id = f"{study_id}_sequenced"
            
            params = {
                'sampleListId': sample_list_id,
                'entrezGeneId': entrez_id,
                'projection': 'DETAILED'
            }
            
            mutations_response = requests.get(
                f"{base_url}/molecular-profiles/{profile_id}/mutations",
                params=params
            )
            
            if mutations_response.status_code == 200:
                mutations = mutations_response.json()
                if mutations:
                    results[gene] = len(mutations)
                    print(f"  ✅ {gene}: {len(mutations)} mutations")
                    
        except Exception as e:
            print(f"  ⚠️ {gene}: Error - {e}")
            continue
    
    return results

def main():
    """
    Discover mutation-rich genes across major cancer studies
    """
    print("🚀 SIMPLE GENE DISCOVERY")
    print("=" * 50)
    print("Finding frequently mutated genes in major cancer studies")
    
    # Studies to check
    studies = [
        'gbm_tcga_pan_can_atlas_2018',
        'brca_tcga_pan_can_atlas_2018',
        'luad_tcga_pan_can_atlas_2018',
        'coadread_tcga_pan_can_atlas_2018',
        'paad_tcga_pan_can_atlas_2018',
        'skcm_tcga_pan_can_atlas_2018',
        'prad_tcga_pan_can_atlas_2018',
        'ov_tcga_pan_can_atlas_2018'
    ]
    
    # Common cancer genes to check
    cancer_genes = [
        'TP53', 'KRAS', 'PIK3CA', 'PTEN', 'APC', 'BRCA1', 'BRCA2',
        'EGFR', 'MYC', 'RB1', 'NF1', 'ATM', 'CDKN2A', 'BRAF',
        'IDH1', 'IDH2', 'ARID1A', 'CTNNB1', 'FBXW7', 'NRAS',
        'SMAD4', 'VHL', 'TSC1', 'TSC2', 'STK11', 'KEAP1'
    ]
    
    all_results = {}
    
    for study_id in studies:
        study_results = get_mutations_for_study(study_id, cancer_genes)
        if study_results:
            all_results[study_id] = study_results
    
    # Generate recommendations
    print("\n" + "=" * 60)
    print("🎯 RESEARCH QUESTION RECOMMENDATIONS")
    print("=" * 60)
    
    recommendations = []
    
    for study_id, gene_mutations in all_results.items():
        cancer_type = study_id.split('_')[0].upper()
        
        # Sort genes by mutation count
        sorted_genes = sorted(gene_mutations.items(), key=lambda x: x[1], reverse=True)
        
        print(f"\n{cancer_type} ({study_id}):")
        for gene, count in sorted_genes[:5]:
            print(f"  {gene}: {count} mutations")
            
            # Generate research question
            if count > 50:
                question = f"How do {gene} mutations create de novo enhancers in {cancer_type.lower()} cancer?"
                priority = "HIGH"
            elif count > 20:
                question = f"What tissue-specific regulatory elements are disrupted by {gene} variants in {cancer_type.lower()}?"
                priority = "MEDIUM"
            else:
                question = f"How do {gene} mutations affect regulatory networks in {cancer_type.lower()}?"
                priority = "LOW"
            
            recommendations.append({
                'question': question,
                'gene': gene,
                'cancer_type': cancer_type.lower(),
                'mutation_count': count,
                'study_id': study_id,
                'priority': priority
            })
    
    # Sort all recommendations by mutation count
    recommendations.sort(key=lambda x: x['mutation_count'], reverse=True)
    
    # Save top recommendations
    print("\n" + "=" * 60)
    print("📝 TOP 10 RECOMMENDED RESEARCH QUESTIONS")
    print("=" * 60)
    
    with open('top_research_questions.md', 'w') as f:
        f.write("# Top Research Questions Based on cBioPortal Data\n\n")
        f.write("Generated from TCGA Pan-Cancer Atlas mutation data\n\n")
        
        for i, rec in enumerate(recommendations[:10], 1):
            print(f"\n{i}. {rec['question']}")
            print(f"   📊 {rec['mutation_count']} mutations available in {rec['study_id']}")
            print(f"   🎯 Priority: {rec['priority']}")
            
            f.write(f"## {i}. {rec['question']}\n\n")
            f.write(f"- **Gene**: {rec['gene']}\n")
            f.write(f"- **Cancer Type**: {rec['cancer_type']}\n")
            f.write(f"- **Mutations Available**: {rec['mutation_count']}\n")
            f.write(f"- **Study ID**: {rec['study_id']}\n")
            f.write(f"- **Priority**: {rec['priority']}\n\n")
            f.write("---\n\n")
    
    print(f"\n📁 Full recommendations saved to: top_research_questions.md")
    
    return recommendations

if __name__ == "__main__":
    recommendations = main()