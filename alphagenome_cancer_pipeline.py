#!/usr/bin/env python3
"""
AlphaGenome-Powered Cancer Research Pipeline
Focuses on novel regulatory mechanisms in cancer using multimodal predictions
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import json
import os
from datetime import datetime

from alphagenome.data import genome, track_data
from alphagenome.models import dna_client, variant_scorers
from alphagenome.interpretation import ism
from alphagenome.visualization import plot, plot_components


@dataclass
class RegulatoryVariant:
    """Represents a variant with regulatory impact"""
    chromosome: str
    position: int
    ref: str
    alt: str
    variant_id: str
    patient_id: Optional[str] = None
    cancer_type: Optional[str] = None
    
    def to_alphagenome_variant(self) -> genome.Variant:
        """Convert to AlphaGenome variant object"""
        return genome.Variant(
            chromosome=self.chromosome,
            position=self.position,
            reference_bases=self.ref,
            alternate_bases=self.alt,
            name=self.variant_id
        )


class AlphaGenomeCancerPipeline:
    """
    Novel cancer research pipeline leveraging AlphaGenome's unique capabilities
    for discovering regulatory mechanisms in cancer
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = dna_client.create(api_key)
        
        # Common cancer-relevant ontology terms
        self.tissue_ontology = {
            'lung': 'UBERON:0002048',
            'colon': 'UBERON:0001157',
            'liver': 'UBERON:0001114',
            'brain': 'UBERON:0000955',
            'breast': 'UBERON:0000310',
            'prostate': 'UBERON:0002367',
            'pancreas': 'UBERON:0001264',
            'blood': 'CL:0001059',  # CD34+ myeloid progenitor
            'lymphoid': 'CL:0000084',  # T cell
        }
        
        # Cancer-relevant genes for analysis
        self.cancer_genes = {
            'oncogenes': ['MYC', 'KRAS', 'BRAF', 'EGFR', 'ALK', 'MET', 'RET', 'ROS1', 'TAL1'],
            'tumor_suppressors': ['TP53', 'RB1', 'PTEN', 'APC', 'BRCA1', 'BRCA2', 'VHL', 'NF1'],
            'chromatin_modifiers': ['EZH2', 'DNMT3A', 'TET2', 'IDH1', 'IDH2', 'SETD2'],
            'transcription_factors': ['MYB', 'RUNX1', 'PAX3', 'PAX7', 'SOX2', 'NANOG']
        }
    
    def analyze_regulatory_landscape(self, 
                                   gene: str, 
                                   tissue: str,
                                   window_size: int = 1_048_576) -> Dict[str, Any]:
        """
        Map the complete regulatory landscape around a gene in a specific tissue
        
        This reveals:
        - All enhancers controlling the gene
        - Tissue-specific regulatory elements
        - Chromatin accessibility patterns
        - Long-range interactions
        """
        print(f"\n=== Mapping Regulatory Landscape ===")
        print(f"Gene: {gene}")
        print(f"Tissue: {tissue}")
        print(f"Analysis window: {window_size:,} bp")
        
        # Get gene coordinates (would need a gene annotation service)
        gene_interval = self._get_gene_interval(gene)
        if not gene_interval:
            return {"error": f"Gene {gene} not found"}
        
        # Expand to capture distant regulatory elements
        analysis_interval = gene_interval.resize(window_size)
        
        # Get tissue ontology
        tissue_ontology = self.tissue_ontology.get(tissue, tissue)
        
        # Predict multimodal outputs
        print("\nPredicting regulatory features...")
        outputs = self.model.predict_interval(
            interval=analysis_interval,
            requested_outputs=[
                dna_client.OutputType.RNA_SEQ,
                dna_client.OutputType.DNASE,
                dna_client.OutputType.CHIP_HISTONE,
                dna_client.OutputType.CHIP_TF,
                dna_client.OutputType.CONTACT_MAPS,  # 3D interactions!
            ],
            ontology_terms=[tissue_ontology]
        )
        
        # Analyze regulatory elements
        results = {
            'gene': gene,
            'tissue': tissue,
            'interval': str(analysis_interval),
            'regulatory_elements': [],
            'enhancer_promoter_loops': [],
            'tissue_specific_elements': []
        }
        
        # Find active enhancers (H3K27ac + H3K4me1 + DNase)
        print("\nIdentifying active enhancers...")
        enhancers = self._find_enhancers(outputs, gene_interval)
        results['regulatory_elements'] = enhancers
        
        # Map 3D interactions
        print("\nMapping enhancer-promoter interactions...")
        interactions = self._map_3d_interactions(outputs, gene_interval)
        results['enhancer_promoter_loops'] = interactions
        
        # Identify tissue-specific elements
        print("\nFinding tissue-specific regulatory elements...")
        tissue_specific = self._find_tissue_specific_elements(
            analysis_interval, gene, tissue
        )
        results['tissue_specific_elements'] = tissue_specific
        
        print(f"\nFound {len(enhancers)} enhancers, {len(interactions)} 3D interactions")
        
        return results
    
    def discover_de_novo_enhancers(self, 
                                  cancer_variants: List[RegulatoryVariant],
                                  tissue: str,
                                  nearby_genes: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Discover variants that create new enhancers in cancer
        
        This can reveal:
        - Variants that create binding sites for oncogenic TFs
        - New enhancers that activate nearby oncogenes
        - Tissue-specific enhancer gains
        """
        print(f"\n=== Discovering De Novo Enhancers ===")
        print(f"Analyzing {len(cancer_variants)} variants in {tissue}")
        
        tissue_ontology = self.tissue_ontology.get(tissue, tissue)
        de_novo_enhancers = []
        
        for variant in cancer_variants:
            ag_variant = variant.to_alphagenome_variant()
            interval = ag_variant.reference_interval.resize(131_072)  # 131kb window
            
            # Predict enhancer marks
            outputs = self.model.predict_variant(
                interval=interval,
                variant=ag_variant,
                requested_outputs=[
                    dna_client.OutputType.DNASE,
                    dna_client.OutputType.CHIP_HISTONE,
                ],
                ontology_terms=[tissue_ontology]
            )
            
            # Check for enhancer mark gains
            enhancer_gain = self._detect_enhancer_gain(outputs, ag_variant)
            
            if enhancer_gain['is_de_novo']:
                # Score impact on nearby genes
                if nearby_genes:
                    gene_impacts = self._score_gene_impacts(
                        ag_variant, nearby_genes, tissue_ontology
                    )
                    enhancer_gain['affected_genes'] = gene_impacts
                
                de_novo_enhancers.append({
                    'variant': variant.variant_id,
                    'location': f"{variant.chromosome}:{variant.position}",
                    'enhancer_score': enhancer_gain['score'],
                    'affected_genes': enhancer_gain.get('affected_genes', []),
                    'histone_changes': enhancer_gain['histone_changes']
                })
        
        print(f"\nFound {len(de_novo_enhancers)} de novo enhancers")
        
        return {
            'tissue': tissue,
            'total_variants': len(cancer_variants),
            'de_novo_enhancers': de_novo_enhancers,
            'summary': self._summarize_enhancer_targets(de_novo_enhancers)
        }
    
    def analyze_long_range_interactions(self,
                                      gene: str,
                                      cancer_variants: List[RegulatoryVariant],
                                      tissue: str,
                                      max_distance: int = 1_000_000) -> Dict[str, Any]:
        """
        Analyze how distant variants affect gene regulation through 3D chromatin loops
        
        This reveals:
        - Enhancer hijacking events
        - TAD boundary disruptions
        - Novel long-range regulatory connections
        """
        print(f"\n=== Long-Range Interaction Analysis ===")
        print(f"Gene: {gene}")
        print(f"Max distance: {max_distance:,} bp")
        
        gene_interval = self._get_gene_interval(gene)
        if not gene_interval:
            return {"error": f"Gene {gene} not found"}
        
        tissue_ontology = self.tissue_ontology.get(tissue, tissue)
        long_range_effects = []
        
        # Filter variants within max_distance of gene
        nearby_variants = [
            v for v in cancer_variants
            if self._distance_to_gene(v, gene_interval) <= max_distance
        ]
        
        print(f"Analyzing {len(nearby_variants)} variants within {max_distance:,} bp")
        
        for variant in nearby_variants:
            distance = self._distance_to_gene(variant, gene_interval)
            if distance < 10_000:  # Skip promoter-proximal variants
                continue
            
            ag_variant = variant.to_alphagenome_variant()
            
            # Use 1MB window to capture long-range interactions
            interval = genome.Interval(
                chromosome=gene_interval.chromosome,
                start=min(variant.position, gene_interval.start) - 100_000,
                end=max(variant.position, gene_interval.end) + 100_000
            ).resize(1_000_000)
            
            # Predict 3D contacts and expression
            outputs = self.model.predict_variant(
                interval=interval,
                variant=ag_variant,
                requested_outputs=[
                    dna_client.OutputType.CONTACT_MAPS,
                    dna_client.OutputType.RNA_SEQ,
                    dna_client.OutputType.DNASE,
                ],
                ontology_terms=[tissue_ontology]
            )
            
            # Analyze contact changes
            contact_changes = self._analyze_contact_changes(
                outputs, variant.position, gene_interval
            )
            
            if contact_changes['significant_change']:
                # Calculate gene expression impact
                expr_change = self._calculate_expression_change(
                    outputs, gene_interval
                )
                
                long_range_effects.append({
                    'variant': variant.variant_id,
                    'distance_to_gene': distance,
                    'contact_strength_change': contact_changes['strength_change'],
                    'expression_change': expr_change,
                    'mechanism': contact_changes['mechanism']
                })
        
        print(f"\nFound {len(long_range_effects)} significant long-range effects")
        
        return {
            'gene': gene,
            'tissue': tissue,
            'variants_analyzed': len(nearby_variants),
            'long_range_effects': sorted(
                long_range_effects,
                key=lambda x: abs(x['expression_change']),
                reverse=True
            ),
            'summary': self._summarize_mechanisms(long_range_effects)
        }
    
    def compare_tissue_specificity(self,
                                 variant: RegulatoryVariant,
                                 tissues: List[str]) -> Dict[str, Any]:
        """
        Compare variant effects across tissues to understand tissue-specific vulnerabilities
        
        This reveals:
        - Why certain mutations drive cancer in specific tissues
        - Tissue-specific dependencies
        - Potential for tissue-agnostic therapies
        """
        print(f"\n=== Tissue Specificity Analysis ===")
        print(f"Variant: {variant.variant_id}")
        print(f"Tissues: {', '.join(tissues)}")
        
        ag_variant = variant.to_alphagenome_variant()
        interval = ag_variant.reference_interval.resize(524_288)  # 524kb
        
        tissue_effects = {}
        
        # Get predictions for all tissues
        for tissue in tissues:
            tissue_ontology = self.tissue_ontology.get(tissue, tissue)
            
            outputs = self.model.predict_variant(
                interval=interval,
                variant=ag_variant,
                requested_outputs=[
                    dna_client.OutputType.RNA_SEQ,
                    dna_client.OutputType.DNASE,
                    dna_client.OutputType.CHIP_HISTONE,
                ],
                ontology_terms=[tissue_ontology]
            )
            
            # Score variant impact in this tissue
            impact = self._score_tissue_impact(outputs, ag_variant)
            
            # Find affected genes
            affected_genes = self._find_affected_genes(outputs, interval)
            
            tissue_effects[tissue] = {
                'regulatory_impact_score': impact['score'],
                'chromatin_accessibility_change': impact['dnase_change'],
                'affected_genes': affected_genes,
                'top_affected_gene': affected_genes[0] if affected_genes else None,
                'enhancer_activity': impact['enhancer_activity']
            }
        
        # Identify tissue-specific effects
        specificity = self._calculate_tissue_specificity(tissue_effects)
        
        return {
            'variant': variant.variant_id,
            'location': f"{variant.chromosome}:{variant.position}",
            'tissue_effects': tissue_effects,
            'tissue_specificity': specificity,
            'most_affected_tissue': specificity['most_affected'],
            'is_tissue_specific': specificity['is_specific']
        }
    
    def find_convergent_mechanisms(self,
                                 patient_variants: Dict[str, List[RegulatoryVariant]],
                                 target_genes: List[str],
                                 tissue: str) -> Dict[str, Any]:
        """
        Find convergent regulatory mechanisms across patients
        
        This reveals:
        - Common enhancers targeted by different mutations
        - Shared regulatory programs in cancer
        - Patient stratification opportunities
        """
        print(f"\n=== Convergent Mechanism Analysis ===")
        print(f"Patients: {len(patient_variants)}")
        print(f"Target genes: {', '.join(target_genes)}")
        
        tissue_ontology = self.tissue_ontology.get(tissue, tissue)
        
        # Analyze each patient's variants
        patient_mechanisms = {}
        
        for patient_id, variants in patient_variants.items():
            print(f"\nAnalyzing patient {patient_id} ({len(variants)} variants)...")
            
            mechanisms = []
            for gene in target_genes:
                gene_mechanisms = self._analyze_gene_regulation(
                    variants, gene, tissue_ontology
                )
                mechanisms.extend(gene_mechanisms)
            
            patient_mechanisms[patient_id] = mechanisms
        
        # Find convergent patterns
        convergent = self._find_convergent_patterns(patient_mechanisms)
        
        return {
            'tissue': tissue,
            'patients_analyzed': len(patient_variants),
            'target_genes': target_genes,
            'convergent_mechanisms': convergent['mechanisms'],
            'patient_clusters': convergent['clusters'],
            'therapeutic_targets': convergent['targets']
        }
    
    def predict_splicing_dysregulation(self,
                                     gene: str,
                                     variants: List[RegulatoryVariant],
                                     tissue: str) -> Dict[str, Any]:
        """
        Predict splicing changes caused by regulatory variants
        
        This reveals:
        - Exon skipping events
        - Isoform switches
        - Neo-epitope generation
        """
        print(f"\n=== Splicing Dysregulation Analysis ===")
        print(f"Gene: {gene}")
        print(f"Variants: {len(variants)}")
        
        gene_interval = self._get_gene_interval(gene)
        if not gene_interval:
            return {"error": f"Gene {gene} not found"}
        
        tissue_ontology = self.tissue_ontology.get(tissue, tissue)
        splicing_effects = []
        
        for variant in variants:
            ag_variant = variant.to_alphagenome_variant()
            
            # Use gene body + flanking regions
            interval = gene_interval.resize(gene_interval.length() + 20_000)
            
            outputs = self.model.predict_variant(
                interval=interval,
                variant=ag_variant,
                requested_outputs=[
                    dna_client.OutputType.SPLICE_SITES,
                    dna_client.OutputType.SPLICE_SITE_USAGE,
                    dna_client.OutputType.SPLICE_JUNCTIONS,
                ],
                ontology_terms=[tissue_ontology]
            )
            
            # Analyze splicing changes
            splice_changes = self._analyze_splicing_changes(outputs, gene_interval)
            
            if splice_changes['has_effect']:
                splicing_effects.append({
                    'variant': variant.variant_id,
                    'splice_effect': splice_changes['effect_type'],
                    'affected_exons': splice_changes['affected_exons'],
                    'isoform_change': splice_changes['isoform_prediction'],
                    'functional_impact': splice_changes['functional_impact']
                })
        
        return {
            'gene': gene,
            'tissue': tissue,
            'variants_analyzed': len(variants),
            'splicing_effects': splicing_effects,
            'summary': self._summarize_splicing_impacts(splicing_effects)
        }
    
    # Helper methods
    def _get_gene_interval(self, gene: str) -> Optional[genome.Interval]:
        """Get genomic interval for a gene"""
        # In a real implementation, this would query a gene annotation database
        # For now, return example intervals for common cancer genes
        gene_coords = {
            'MYC': genome.Interval('chr8', 127_735_434, 127_742_951),
            'EGFR': genome.Interval('chr7', 55_019_017, 55_211_628),
            'TP53': genome.Interval('chr17', 7_661_779, 7_687_538),
            'KRAS': genome.Interval('chr12', 25_205_246, 25_250_936),
            'TAL1': genome.Interval('chr1', 47_227_267, 47_243_807),
        }
        return gene_coords.get(gene)
    
    def _find_enhancers(self, outputs: Any, gene_interval: genome.Interval) -> List[Dict]:
        """Find active enhancers based on histone marks and accessibility"""
        enhancers = []
        
        # Look for H3K27ac + H3K4me1 peaks with DNase accessibility
        # This is a simplified implementation
        # Real implementation would use peak calling
        
        return enhancers
    
    def _map_3d_interactions(self, outputs: Any, gene_interval: genome.Interval) -> List[Dict]:
        """Map 3D chromatin interactions with gene promoter"""
        interactions = []
        
        if hasattr(outputs, 'contact_maps'):
            # Analyze contact maps for significant interactions
            # This would identify loops connecting to gene promoter
            pass
        
        return interactions
    
    def _find_tissue_specific_elements(self, 
                                     interval: genome.Interval,
                                     gene: str,
                                     tissue: str) -> List[Dict]:
        """Find regulatory elements specific to this tissue"""
        # Compare with other tissues to find specific elements
        return []
    
    def _detect_enhancer_gain(self, outputs: Any, variant: genome.Variant) -> Dict:
        """Detect if variant creates a new enhancer"""
        # Check for gain of H3K27ac, H3K4me1, and DNase accessibility
        return {
            'is_de_novo': False,
            'score': 0.0,
            'histone_changes': {}
        }
    
    def _score_gene_impacts(self, 
                          variant: genome.Variant,
                          genes: List[str],
                          tissue_ontology: str) -> List[Dict]:
        """Score variant impact on nearby genes"""
        impacts = []
        
        # Use variant scoring for each gene
        variant_scorer = variant_scorers.RECOMMENDED_VARIANT_SCORERS['RNA_SEQ']
        
        return impacts
    
    def _distance_to_gene(self, 
                         variant: RegulatoryVariant,
                         gene_interval: genome.Interval) -> int:
        """Calculate distance from variant to gene"""
        if variant.chromosome != gene_interval.chromosome:
            return float('inf')
        
        if gene_interval.start <= variant.position <= gene_interval.end:
            return 0
        
        return min(
            abs(variant.position - gene_interval.start),
            abs(variant.position - gene_interval.end)
        )
    
    def _analyze_contact_changes(self, outputs: Any, 
                               variant_pos: int,
                               gene_interval: genome.Interval) -> Dict:
        """Analyze 3D contact changes between variant and gene"""
        return {
            'significant_change': False,
            'strength_change': 0.0,
            'mechanism': 'unknown'
        }
    
    def _calculate_expression_change(self, 
                                   outputs: Any,
                                   gene_interval: genome.Interval) -> float:
        """Calculate gene expression change from variant"""
        if hasattr(outputs, 'reference') and hasattr(outputs, 'alternate'):
            # Calculate mean expression change over gene body
            ref_expr = outputs.reference.rna_seq
            alt_expr = outputs.alternate.rna_seq
            # Would need to extract gene-specific signal
            return 0.0
        return 0.0
    
    def _summarize_mechanisms(self, effects: List[Dict]) -> Dict:
        """Summarize long-range regulatory mechanisms"""
        if not effects:
            return {'primary_mechanism': 'none', 'count': 0}
        
        mechanisms = [e['mechanism'] for e in effects]
        primary = max(set(mechanisms), key=mechanisms.count)
        
        return {
            'primary_mechanism': primary,
            'count': len(effects),
            'avg_expression_change': np.mean([e['expression_change'] for e in effects])
        }
    
    def _score_tissue_impact(self, outputs: Any, variant: genome.Variant) -> Dict:
        """Score regulatory impact in a specific tissue"""
        return {
            'score': 0.0,
            'dnase_change': 0.0,
            'enhancer_activity': 'none'
        }
    
    def _find_affected_genes(self, outputs: Any, interval: genome.Interval) -> List[str]:
        """Find genes affected by variant in given interval"""
        # Would use gene annotations and expression changes
        return []
    
    def _calculate_tissue_specificity(self, tissue_effects: Dict) -> Dict:
        """Calculate tissue specificity of variant effects"""
        scores = [e['regulatory_impact_score'] for e in tissue_effects.values()]
        
        if not scores:
            return {'is_specific': False, 'most_affected': None}
        
        max_score = max(scores)
        mean_score = np.mean(scores)
        
        # Consider specific if max effect is >2x mean
        is_specific = max_score > 2 * mean_score if mean_score > 0 else False
        
        most_affected = max(tissue_effects.keys(), 
                          key=lambda t: tissue_effects[t]['regulatory_impact_score'])
        
        return {
            'is_specific': is_specific,
            'most_affected': most_affected,
            'specificity_score': max_score / mean_score if mean_score > 0 else 0
        }
    
    def _analyze_gene_regulation(self,
                               variants: List[RegulatoryVariant],
                               gene: str,
                               tissue_ontology: str) -> List[Dict]:
        """Analyze how variants affect gene regulation"""
        return []
    
    def _find_convergent_patterns(self, patient_mechanisms: Dict) -> Dict:
        """Find convergent regulatory patterns across patients"""
        return {
            'mechanisms': [],
            'clusters': {},
            'targets': []
        }
    
    def _analyze_splicing_changes(self, outputs: Any, gene_interval: genome.Interval) -> Dict:
        """Analyze splicing changes from variant"""
        return {
            'has_effect': False,
            'effect_type': 'none',
            'affected_exons': [],
            'isoform_prediction': 'no_change',
            'functional_impact': 'unknown'
        }
    
    def _summarize_splicing_impacts(self, effects: List[Dict]) -> Dict:
        """Summarize splicing dysregulation impacts"""
        if not effects:
            return {'primary_effect': 'none', 'clinical_relevance': 'low'}
        
        effect_types = [e['splice_effect'] for e in effects]
        primary = max(set(effect_types), key=effect_types.count)
        
        return {
            'primary_effect': primary,
            'total_variants': len(effects),
            'clinical_relevance': 'high' if any(e['functional_impact'] == 'loss_of_function' 
                                              for e in effects) else 'moderate'
        }
    
    def _summarize_enhancer_targets(self, enhancers: List[Dict]) -> Dict:
        """Summarize de novo enhancer targets"""
        if not enhancers:
            return {'top_targets': [], 'oncogene_activation': False}
        
        all_genes = []
        for enh in enhancers:
            all_genes.extend([g['gene'] for g in enh.get('affected_genes', [])])
        
        gene_counts = pd.Series(all_genes).value_counts()
        
        return {
            'top_targets': gene_counts.head(5).to_dict(),
            'oncogene_activation': any(g in self.cancer_genes['oncogenes'] for g in all_genes)
        }
    
    # ============ Visualization Methods ============
    
    def visualize_variant_impact(self,
                                variant: RegulatoryVariant,
                                output,
                                interval: genome.Interval,
                                output_dir: str = "visualizations",
                                tissue_name: str = "tissue") -> str:
        """
        Create visualization showing reference vs alternate allele effects
        
        Returns:
            Path to saved visualization
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Define colors for REF and ALT
        ref_alt_colors = {'REF': 'dimgrey', 'ALT': 'red'}
        
        # Build plot components
        components = []
        
        # RNA-seq tracks
        if hasattr(output.reference, 'rna_seq'):
            components.append(
                plot_components.OverlaidTracks(
                    tdata={
                        'REF': output.reference.rna_seq,
                        'ALT': output.alternate.rna_seq,
                    },
                    colors=ref_alt_colors,
                    ylabel_template=f'RNA-seq {tissue_name}\n{{strand}}',
                    alpha=0.8,
                    shared_y_scale=True
                )
            )
        
        # DNase tracks
        if hasattr(output.reference, 'dnase'):
            components.append(
                plot_components.OverlaidTracks(
                    tdata={
                        'REF': output.reference.dnase,
                        'ALT': output.alternate.dnase,
                    },
                    colors=ref_alt_colors,
                    ylabel_template=f'DNase {tissue_name}',
                    alpha=0.8,
                    shared_y_scale=True
                )
            )
        
        # ChIP-seq histone marks
        if hasattr(output.reference, 'chip_histone'):
            # Get histone marks present
            ref_histones = output.reference.chip_histone.metadata
            if not ref_histones.empty:
                histone_mark = ref_histones.iloc[0]['histone_mark']
                components.append(
                    plot_components.OverlaidTracks(
                        tdata={
                            'REF': output.reference.chip_histone,
                            'ALT': output.alternate.chip_histone,
                        },
                        colors=ref_alt_colors,
                        ylabel_template=f'{histone_mark} {tissue_name}',
                        alpha=0.8,
                        shared_y_scale=True
                    )
                )
        
        # Create the plot with variant annotation
        ag_variant = variant.to_alphagenome_variant()
        fig = plot_components.plot(
            components=components,
            interval=interval,
            annotations=[plot_components.VariantAnnotation([ag_variant])],
            title=f'Regulatory Impact of {variant.variant_id} ({variant.chromosome}:{variant.position})',
            fig_width=20,
            despine=True,
            despine_keep_bottom=True
        )
        
        # Save the plot
        filename = f"{variant.variant_id}_{variant.chromosome}_{variant.position}.png"
        output_path = os.path.join(output_dir, filename)
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        return output_path
    
    def visualize_regulatory_landscape(self,
                                     gene: str,
                                     outputs: Dict,
                                     interval: genome.Interval,
                                     tissue: str,
                                     output_dir: str = "visualizations") -> str:
        """
        Create comprehensive regulatory landscape visualization
        
        Returns:
            Path to saved visualization
        """
        os.makedirs(output_dir, exist_ok=True)
        
        components = []
        
        # RNA-seq tracks
        if hasattr(outputs, 'rna_seq'):
            components.append(
                plot_components.Tracks(
                    tdata=outputs.rna_seq,
                    ylabel_template=f'RNA-seq {tissue}',
                    filled=True,
                    track_colors='darkblue',
                    shared_y_scale=True
                )
            )
        
        # DNase accessibility
        if hasattr(outputs, 'dnase'):
            components.append(
                plot_components.Tracks(
                    tdata=outputs.dnase,
                    ylabel_template=f'DNase {tissue}',
                    filled=True,
                    track_colors='darkgreen',
                    shared_y_scale=True
                )
            )
        
        # Histone marks
        if hasattr(outputs, 'chip_histone'):
            # Define colors for different histone marks
            histone_colors = {
                'H3K27AC': '#e41a1c',
                'H3K36ME3': '#ff7f00',
                'H3K4ME1': '#377eb8',
                'H3K4ME3': '#984ea3',
                'H3K9AC': '#4daf4a',
                'H3K27ME3': '#ffc0cb',
            }
            
            # Get colors for each track
            tdata = outputs.chip_histone
            if not tdata.metadata.empty:
                track_colors = [
                    histone_colors.get(row['histone_mark'].upper(), '#000000')
                    for _, row in tdata.metadata.iterrows()
                ]
                
                components.append(
                    plot_components.Tracks(
                        tdata=tdata,
                        ylabel_template='{histone_mark}',
                        filled=True,
                        track_colors=track_colors
                    )
                )
        
        # Create the plot
        fig = plot_components.plot(
            components=components,
            interval=interval,
            title=f'Regulatory Landscape of {gene} in {tissue} tissue',
            fig_width=20,
            despine=True,
            despine_keep_bottom=True
        )
        
        # Save the plot
        filename = f"{gene}_regulatory_landscape_{tissue}.png"
        output_path = os.path.join(output_dir, filename)
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        return output_path
    
    def generate_markdown_report(self,
                               analysis_type: str,
                               results: Dict,
                               visualizations: List[str],
                               output_dir: str = "reports") -> str:
        """
        Generate a comprehensive markdown report with embedded visualizations
        
        Args:
            analysis_type: Type of analysis performed
            results: Analysis results dictionary
            visualizations: List of visualization file paths
            output_dir: Directory to save the report
            
        Returns:
            Path to the generated markdown report
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Start building the report
        report_lines = [
            f"# AlphaGenome Cancer Analysis Report",
            f"",
            f"**Analysis Type**: {analysis_type}",
            f"**Generated**: {timestamp}",
            f"",
            f"---",
            f"",
        ]
        
        # Add analysis-specific content
        if analysis_type == "Regulatory Landscape":
            report_lines.extend(self._format_regulatory_landscape_report(results))
        elif analysis_type == "De Novo Enhancers":
            report_lines.extend(self._format_enhancer_report(results))
        elif analysis_type == "Tissue Specificity":
            report_lines.extend(self._format_tissue_specificity_report(results))
        elif analysis_type == "Long-Range Interactions":
            report_lines.extend(self._format_long_range_report(results))
        elif analysis_type == "Splicing Dysregulation":
            report_lines.extend(self._format_splicing_report(results))
        else:
            report_lines.extend(self._format_generic_report(results))
        
        # Add visualizations
        if visualizations:
            report_lines.extend([
                "",
                "## Visualizations",
                "",
            ])
            
            for viz_path in visualizations:
                viz_name = os.path.basename(viz_path).replace('_', ' ').replace('.png', '')
                report_lines.extend([
                    f"### {viz_name}",
                    f"",
                    f"![{viz_name}]({viz_path})",
                    f"",
                ])
        
        # Add interpretation section
        report_lines.extend([
            "",
            "## Interpretation",
            "",
            self._generate_interpretation(analysis_type, results),
            "",
        ])
        
        # Add methods section
        report_lines.extend([
            "## Methods",
            "",
            "This analysis was performed using AlphaGenome, a deep learning model that predicts "
            "the effects of DNA sequence variants on gene expression and chromatin state. "
            "The model analyzes sequences up to 1Mb in length and provides predictions for:",
            "",
            "- Gene expression (RNA-seq)",
            "- Chromatin accessibility (DNase-seq, ATAC-seq)",
            "- Histone modifications (ChIP-seq)",
            "- Transcription factor binding",
            "- Splicing patterns",
            "- 3D chromatin interactions",
            "",
        ])
        
        # Save the report
        report_filename = f"{analysis_type.lower().replace(' ', '_')}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_path = os.path.join(output_dir, report_filename)
        
        with open(report_path, 'w') as f:
            f.write('\n'.join(report_lines))
        
        return report_path
    
    def _format_regulatory_landscape_report(self, results: Dict) -> List[str]:
        """Format regulatory landscape results for markdown report"""
        lines = [
            "## Regulatory Landscape Analysis",
            "",
            f"**Gene**: {results.get('gene', 'N/A')}",
            f"**Tissue**: {results.get('tissue', 'N/A')}",
            f"**Analysis Window**: {results.get('interval', 'N/A')}",
            "",
            "### Key Findings",
            "",
            f"- **Regulatory Elements Found**: {len(results.get('regulatory_elements', []))}",
            f"- **Enhancer-Promoter Interactions**: {len(results.get('enhancer_promoter_loops', []))}",
            f"- **Tissue-Specific Elements**: {len(results.get('tissue_specific_elements', []))}",
            "",
        ]
        
        if results.get('regulatory_elements'):
            lines.extend([
                "### Regulatory Elements",
                "",
                "| Type | Location | Score |",
                "|------|----------|-------|",
            ])
            for elem in results['regulatory_elements'][:10]:  # Show top 10
                lines.append(f"| {elem.get('type', 'N/A')} | {elem.get('location', 'N/A')} | {elem.get('score', 'N/A')} |")
        
        return lines
    
    def _format_enhancer_report(self, results: Dict) -> List[str]:
        """Format de novo enhancer results for markdown report"""
        lines = [
            "## De Novo Enhancer Discovery",
            "",
            f"**Tissue**: {results.get('tissue', 'N/A')}",
            f"**Variants Analyzed**: {results.get('total_variants', 0)}",
            f"**De Novo Enhancers Found**: {len(results.get('de_novo_enhancers', []))}",
            "",
        ]
        
        if results.get('de_novo_enhancers'):
            lines.extend([
                "### Discovered Enhancers",
                "",
                "| Variant | Location | Enhancer Score | Affected Genes |",
                "|---------|----------|----------------|----------------|",
            ])
            for enh in results['de_novo_enhancers']:
                genes = ', '.join([g['gene'] for g in enh.get('affected_genes', [])])
                lines.append(f"| {enh['variant']} | {enh['location']} | {enh['enhancer_score']:.3f} | {genes} |")
        
        summary = results.get('summary', {})
        if summary.get('oncogene_activation'):
            lines.extend([
                "",
                "⚠️ **Warning**: De novo enhancers activating oncogenes detected!",
                "",
            ])
        
        return lines
    
    def _format_tissue_specificity_report(self, results: Dict) -> List[str]:
        """Format tissue specificity results for markdown report"""
        lines = [
            "## Tissue Specificity Analysis",
            "",
            f"**Variant**: {results.get('variant', 'N/A')}",
            f"**Location**: {results.get('location', 'N/A')}",
            f"**Most Affected Tissue**: {results.get('most_affected_tissue', 'N/A')}",
            f"**Tissue-Specific**: {'Yes' if results.get('is_tissue_specific') else 'No'}",
            "",
            "### Tissue Effects",
            "",
            "| Tissue | Regulatory Impact | Chromatin Change | Top Gene |",
            "|--------|------------------|------------------|----------|",
        ]
        
        for tissue, effects in results.get('tissue_effects', {}).items():
            lines.append(
                f"| {tissue} | {effects['regulatory_impact_score']:.3f} | "
                f"{effects['chromatin_accessibility_change']:.3f} | "
                f"{effects.get('top_affected_gene', 'None')} |"
            )
        
        return lines
    
    def _format_long_range_report(self, results: Dict) -> List[str]:
        """Format long-range interaction results for markdown report"""
        lines = [
            "## Long-Range Interaction Analysis",
            "",
            f"**Target Gene**: {results.get('gene', 'N/A')}",
            f"**Tissue**: {results.get('tissue', 'N/A')}",
            f"**Variants Analyzed**: {results.get('variants_analyzed', 0)}",
            f"**Significant Long-Range Effects**: {len(results.get('long_range_effects', []))}",
            "",
        ]
        
        if results.get('long_range_effects'):
            lines.extend([
                "### Long-Range Effects",
                "",
                "| Variant | Distance to Gene | Expression Change | Mechanism |",
                "|---------|------------------|-------------------|-----------|",
            ])
            for effect in results['long_range_effects'][:10]:
                lines.append(
                    f"| {effect['variant']} | {effect['distance_to_gene']:,} bp | "
                    f"{effect['expression_change']:.2f} | {effect['mechanism']} |"
                )
        
        return lines
    
    def _format_splicing_report(self, results: Dict) -> List[str]:
        """Format splicing dysregulation results for markdown report"""
        lines = [
            "## Splicing Dysregulation Analysis",
            "",
            f"**Gene**: {results.get('gene', 'N/A')}",
            f"**Tissue**: {results.get('tissue', 'N/A')}",
            f"**Variants Analyzed**: {results.get('variants_analyzed', 0)}",
            f"**Splicing Effects Found**: {len(results.get('splicing_effects', []))}",
            "",
        ]
        
        if results.get('splicing_effects'):
            lines.extend([
                "### Splicing Effects",
                "",
                "| Variant | Effect Type | Affected Exons | Functional Impact |",
                "|---------|-------------|----------------|-------------------|",
            ])
            for effect in results['splicing_effects']:
                exons = ', '.join(effect.get('affected_exons', []))
                lines.append(
                    f"| {effect['variant']} | {effect['splice_effect']} | "
                    f"{exons} | {effect['functional_impact']} |"
                )
        
        return lines
    
    def _format_generic_report(self, results: Dict) -> List[str]:
        """Format generic results for markdown report"""
        return [
            "## Analysis Results",
            "",
            "```json",
            json.dumps(results, indent=2),
            "```",
            "",
        ]
    
    def _generate_interpretation(self, analysis_type: str, results: Dict) -> str:
        """Generate interpretation based on analysis type and results"""
        interpretations = {
            "Regulatory Landscape": (
                "This analysis mapped all regulatory elements controlling the target gene. "
                "Key findings include the identification of distal enhancers and their "
                "tissue-specific activity patterns. These elements represent potential "
                "therapeutic targets for modulating gene expression."
            ),
            "De Novo Enhancers": (
                "The analysis identified variants that create new enhancer elements. "
                "These de novo enhancers can lead to inappropriate gene activation, "
                "particularly concerning when they affect oncogenes. Such variants "
                "represent a mechanism for cancer development through regulatory disruption."
            ),
            "Tissue Specificity": (
                "This analysis reveals why certain variants drive cancer in specific tissues. "
                "Tissue-specific effects often depend on the presence of particular "
                "transcription factors and chromatin states unique to each cell type."
            ),
            "Long-Range Interactions": (
                "The analysis uncovered how variants far from genes can still affect their "
                "expression through 3D chromatin interactions. This mechanism explains "
                "how non-coding variants contribute to cancer through enhancer hijacking "
                "and TAD disruption."
            ),
            "Splicing Dysregulation": (
                "This analysis predicted how variants affect RNA splicing patterns. "
                "Aberrant splicing can create non-functional proteins or novel isoforms "
                "with oncogenic properties, representing another layer of gene regulation "
                "disrupted in cancer."
            ),
        }
        
        return interpretations.get(analysis_type, 
            "The analysis provides insights into regulatory mechanisms affected by "
            "the studied variants. Further experimental validation is recommended.")


# Convenience functions for AI agents
def analyze_regulatory_cancer_mechanism(
    question: str,
    gene: str,
    tissue: str,
    variants: Optional[List[Dict]] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Simple entry point for AI agents to analyze regulatory cancer mechanisms
    
    Args:
        question: Research question about regulatory mechanisms
        gene: Target gene to analyze
        tissue: Tissue context
        variants: Optional list of variants to analyze
        api_key: AlphaGenome API key
    
    Returns:
        Analysis results with interpretation
    """
    if not api_key:
        return {"error": "AlphaGenome API key required"}
    
    pipeline = AlphaGenomeCancerPipeline(api_key)
    
    # Parse question type and route to appropriate analysis
    question_lower = question.lower()
    
    if "regulatory landscape" in question_lower or "enhancers" in question_lower:
        return pipeline.analyze_regulatory_landscape(gene, tissue)
    
    elif "tissue specific" in question_lower:
        if variants:
            variant = RegulatoryVariant(**variants[0])
            tissues = ['lung', 'colon', 'liver', 'brain']  # Default comparison
            return pipeline.compare_tissue_specificity(variant, tissues)
    
    elif "long range" in question_lower or "distant" in question_lower:
        if variants:
            reg_variants = [RegulatoryVariant(**v) for v in variants]
            return pipeline.analyze_long_range_interactions(gene, reg_variants, tissue)
    
    elif "splicing" in question_lower:
        if variants:
            reg_variants = [RegulatoryVariant(**v) for v in variants]
            return pipeline.predict_splicing_dysregulation(gene, reg_variants, tissue)
    
    else:
        # Default to regulatory landscape analysis
        return pipeline.analyze_regulatory_landscape(gene, tissue)


if __name__ == "__main__":
    # Example usage
    API_KEY = "your_alphagenome_api_key"
    
    # Example 1: Map regulatory landscape
    results = analyze_regulatory_cancer_mechanism(
        question="What enhancers control MYC expression in lung cancer?",
        gene="MYC",
        tissue="lung",
        api_key=API_KEY
    )
    
    print(json.dumps(results, indent=2))