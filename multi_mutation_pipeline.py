#!/usr/bin/env python3
"""
Multi-Mutation Enhancer Detection Pipeline
==========================================

Advanced pipeline for systematic analysis of multiple mutations to detect enhancers.
Features:
- Batch processing of multiple mutations
- Improved enhancer detection logic with statistical validation
- Pattern recognition across mutations
- Comprehensive reporting with aggregated insights
"""

import os
import sys
import json
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent / "modules"))

from mutation_fetchers.cbioportal_fetcher import cBioPortalFetcher
from enhancer_detection.alphagenome_processor import AlphaGenomeOutputProcessor
from reporting.enhancer_reporter import EnhancerReporter

class MultiMutationEnhancerPipeline:
    """
    Advanced pipeline for systematic multi-mutation enhancer detection
    """
    
    def __init__(self, alphagenome_api_key: str):
        """Initialize with AlphaGenome API key"""
        self.alphagenome_api_key = alphagenome_api_key
        
        # Initialize components
        self.mutation_fetcher = cBioPortalFetcher()
        self.alphagenome_processor = AlphaGenomeOutputProcessor(alphagenome_api_key)
        self.reporter = EnhancerReporter()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Tissue ontology mapping
        self.tissue_ontology = {
            'breast': 'UBERON:0000310',
            'pancreatic': 'UBERON:0001264', 
            'lung_adenocarcinoma': 'UBERON:0002048',
            'lung_squamous': 'UBERON:0002048',
            'glioblastoma': 'UBERON:0000955',
            'colorectal': 'UBERON:0001157',
            'prostate': 'UBERON:0002367',
            'ovarian': 'UBERON:0000992',
            'kidney_clear_cell': 'UBERON:0002113',
            'liver': 'UBERON:0002107'
        }
        
        # Enhanced enhancer detection parameters
        self.enhancer_params = {
            'min_accessibility_increase': 0.05,  # Lower threshold for initial detection
            'statistical_significance': 0.05,     # p-value threshold
            'min_histone_change': 5.0,            # Minimum histone signal change
            'min_expression_change': 0.0001,      # Minimum RNA expression change
            'confidence_levels': {
                'high': {'evidence_types': 3, 'min_score': 0.8},
                'moderate': {'evidence_types': 2, 'min_score': 0.5},
                'low': {'evidence_types': 1, 'min_score': 0.3}
            }
        }
        
        # Ensure output directories exist
        Path("reports/multi_mutation").mkdir(parents=True, exist_ok=True)
        Path("data/multi_mutation").mkdir(parents=True, exist_ok=True)
        Path("visualizations/multi_mutation").mkdir(parents=True, exist_ok=True)
    
    def analyze_multiple_mutations(self, gene: str, cancer_type: str, 
                                  max_mutations: int = 50,
                                  batch_size: int = 5) -> Dict[str, Any]:
        """
        Analyze multiple mutations in batch mode for enhanced pattern detection
        """
        print("="*80)
        print("🧬 MULTI-MUTATION ENHANCER DETECTION PIPELINE")
        print("="*80)
        print(f"Gene: {gene}")
        print(f"Cancer Type: {cancer_type}")
        print(f"Max Mutations: {max_mutations}")
        print(f"Batch Size: {batch_size}")
        print(f"Analysis Mode: Statistical Pattern Recognition")
        print()
        
        research_question = f"Do {gene} mutations systematically create enhancer networks in {cancer_type} cancer?"
        print(f"Research Question: {research_question}")
        print()
        
        # Step 1: Fetch mutations (all at once)
        print("Step 1: Fetching mutations from cBioPortal...")
        mutation_data = self.mutation_fetcher.fetch_mutations(gene, cancer_type, max_mutations)
        
        if mutation_data['status'] != 'success':
            print(f"❌ Failed to fetch mutations: {mutation_data.get('error', 'Unknown error')}")
            return {
                'status': 'failed',
                'stage': 'mutation_fetching',
                'error': mutation_data.get('error', 'Unknown error')
            }
        
        mutations = mutation_data['mutations']
        if not mutations:
            print("❌ No mutations found for this gene/cancer combination")
            return {
                'status': 'failed',
                'stage': 'no_mutations',
                'error': f'No {gene} mutations found in {cancer_type} cancer'
            }
        
        print(f"✅ Found {len(mutations)} mutations to analyze")
        
        # Group mutations by unique variants for efficiency
        unique_variants = self._group_mutations_by_variant(mutations)
        print(f"📊 Grouped into {len(unique_variants)} unique variants")
        
        # Step 2: Get tissue ontology
        tissue_ontology = self.tissue_ontology.get(cancer_type, 'UBERON:0000479')
        print(f"🔬 Using tissue ontology: {tissue_ontology}")
        
        # Step 3: Batch process mutations with AlphaGenome
        print(f"\nStep 3: Batch processing mutations with AlphaGenome...")
        all_results = self._batch_process_mutations(unique_variants, tissue_ontology, batch_size)
        
        # Step 4: Statistical analysis across all mutations
        print(f"\nStep 4: Performing statistical analysis across {len(all_results)} variants...")
        statistical_analysis = self._perform_statistical_analysis(all_results)
        
        # Step 5: Pattern recognition for enhancer networks
        print(f"\nStep 5: Detecting enhancer network patterns...")
        enhancer_patterns = self._detect_enhancer_patterns(all_results, statistical_analysis)
        
        # Step 6: Generate comprehensive report
        print(f"\nStep 6: Generating comprehensive multi-mutation report...")
        report_data = self._generate_comprehensive_report(
            mutation_data, all_results, statistical_analysis, 
            enhancer_patterns, research_question
        )
        
        # Step 7: Create advanced visualizations
        print(f"\nStep 7: Creating advanced visualizations...")
        visualization_files = self._create_advanced_visualizations(
            all_results, statistical_analysis, enhancer_patterns, gene, cancer_type
        )
        
        # Save all data
        self._save_analysis_data(mutation_data, all_results, statistical_analysis, 
                                enhancer_patterns, gene, cancer_type)
        
        # Summarize results
        successful_analyses = [r for r in all_results if r.get('status') == 'success']
        total_enhancers = sum(r.get('enhancers_detected', 0) for r in successful_analyses)
        enhancer_positive_variants = len([r for r in successful_analyses if r.get('enhancers_detected', 0) > 0])
        
        print(f"\n" + "="*80)
        print("🎯 MULTI-MUTATION ANALYSIS COMPLETE!")
        print("="*80)
        print(f"Research Question: {research_question}")
        
        if total_enhancers > 0:
            print(f"✅ ANSWER: YES - {total_enhancers} enhancer(s) detected across variants")
            print(f"📊 Enhancer-creating variants: {enhancer_positive_variants}/{len(successful_analyses)}")
            if enhancer_patterns.get('network_detected', False):
                print(f"🌐 ENHANCER NETWORK DETECTED: {enhancer_patterns.get('network_description', '')}")
        else:
            print(f"❌ ANSWER: NO - No systematic enhancer creation detected")
        
        print(f"📄 Report: {report_data['report_file']}")
        print(f"📊 Visualizations: {len(visualization_files)} files created")
        print(f"🔬 Statistical confidence: {statistical_analysis.get('overall_confidence', 'N/A')}")
        
        return {
            'status': 'success',
            'research_question': research_question,
            'gene': gene,
            'cancer_type': cancer_type,
            'mutations_analyzed': len(successful_analyses),
            'unique_variants': len(unique_variants),
            'total_enhancers_detected': total_enhancers,
            'enhancer_positive_variants': enhancer_positive_variants,
            'enhancer_network_detected': enhancer_patterns.get('network_detected', False),
            'statistical_confidence': statistical_analysis.get('overall_confidence', 'N/A'),
            'report_file': report_data['report_file'],
            'visualization_files': visualization_files
        }
    
    def _group_mutations_by_variant(self, mutations: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group mutations by unique variant (position+ref+alt)"""
        unique_variants = {}
        
        for mutation in mutations:
            # Create unique key for variant
            variant_key = f"{mutation['chromosome']}:{mutation['position']}:{mutation['ref']}>{mutation['alt']}"
            
            if variant_key not in unique_variants:
                unique_variants[variant_key] = []
            
            unique_variants[variant_key].append(mutation)
        
        return unique_variants
    
    def _batch_process_mutations(self, unique_variants: Dict[str, List[Dict[str, Any]]], 
                                tissue_ontology: str, batch_size: int) -> List[Dict[str, Any]]:
        """Process mutations in batches for efficiency"""
        all_results = []
        
        # Convert dict to list for processing
        variant_list = []
        for variant_key, mutations in unique_variants.items():
            # Use the first mutation as representative
            variant_list.append(mutations[0])
        
        # Process in batches using threading for parallel API calls
        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            futures = []
            
            for i, variant in enumerate(variant_list, 1):
                print(f"   📡 Submitting variant {i}/{len(variant_list)} for analysis...")
                future = executor.submit(
                    self._process_single_variant_enhanced,
                    variant, tissue_ontology, i, len(variant_list)
                )
                futures.append(future)
            
            # Collect results as they complete
            for future in as_completed(futures):
                try:
                    result = future.result()
                    all_results.append(result)
                    
                    # Print progress
                    completed = len(all_results)
                    if result.get('status') == 'success':
                        enhancers = result.get('enhancers_detected', 0)
                        print(f"   ✅ [{completed}/{len(variant_list)}] Analysis complete - {enhancers} enhancer(s) detected")
                    else:
                        print(f"   ❌ [{completed}/{len(variant_list)}] Analysis failed: {result.get('error', 'Unknown')}")
                        
                except Exception as e:
                    print(f"   ❌ Error processing variant: {e}")
                    all_results.append({
                        'status': 'error',
                        'error': str(e),
                        'enhancers_detected': 0
                    })
        
        return all_results
    
    def _process_single_variant_enhanced(self, variant: Dict[str, Any], 
                                        tissue_ontology: str, 
                                        variant_num: int, 
                                        total_variants: int) -> Dict[str, Any]:
        """Enhanced single variant processing with improved detection logic"""
        try:
            # Use existing processor but with enhanced parameters
            result = self.alphagenome_processor.analyze_variant_for_enhancers(
                variant, tissue_ontology
            )
            
            # Apply enhanced detection logic
            if result.get('status') == 'success':
                result = self._apply_enhanced_detection_logic(result)
            
            return result
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'variant_id': variant.get('variant_id', 'Unknown'),
                'enhancers_detected': 0
            }
    
    def _apply_enhanced_detection_logic(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply statistical and multi-evidence based enhancer detection"""
        signal_analysis = result.get('raw_signal_analysis', {})
        
        # Recalculate enhancer detection with improved logic
        enhanced_enhancers = []
        
        # Get all signal types
        histone_analysis = signal_analysis.get('histone', {})
        dnase_analysis = signal_analysis.get('dnase', {})
        rna_analysis = signal_analysis.get('rna', {})
        
        # Statistical validation of DNase peaks
        if dnase_analysis and not dnase_analysis.get('error'):
            ref_data = dnase_analysis.get('reference_accessibility', {})
            alt_data = dnase_analysis.get('alternate_accessibility', {})
            
            ref_array = ref_data.get('actual_data', None)
            alt_array = alt_data.get('actual_data', None)
            
            if ref_array is not None and alt_array is not None:
                # Calculate statistical significance of changes
                diff_array = alt_array - ref_array
                
                # Find statistically significant peaks
                significant_peaks = self._find_significant_peaks(
                    ref_array, alt_array, diff_array
                )
                
                # Create enhancer objects for significant peaks
                for peak in significant_peaks:
                    enhancer_score = self._calculate_enhancer_score(
                        peak, histone_analysis, rna_analysis
                    )
                    
                    if enhancer_score >= self.enhancer_params['confidence_levels']['low']['min_score']:
                        confidence = self._determine_confidence(enhancer_score)
                        
                        enhanced_enhancers.append({
                            'enhancer_id': len(enhanced_enhancers) + 1,
                            'genomic_position': peak['position'],
                            'accessibility_increase': peak['diff_value'],
                            'statistical_significance': peak['p_value'],
                            'enhancer_score': enhancer_score,
                            'confidence': confidence,
                            'evidence_summary': self._summarize_evidence(
                                peak, histone_analysis, rna_analysis
                            )
                        })
        
        # Update result with enhanced detection
        result['enhanced_detection'] = True
        result['enhancers_detected'] = len(enhanced_enhancers)
        result['enhancer_evidence'] = enhanced_enhancers
        
        return result
    
    def _find_significant_peaks(self, ref_array: np.ndarray, 
                               alt_array: np.ndarray, 
                               diff_array: np.ndarray) -> List[Dict[str, Any]]:
        """Find statistically significant accessibility peaks"""
        significant_peaks = []
        
        # Flatten arrays for analysis
        ref_flat = ref_array.flatten()
        alt_flat = alt_array.flatten()
        diff_flat = diff_array.flatten()
        
        # Calculate baseline statistics
        baseline_mean = np.mean(ref_flat)
        baseline_std = np.std(ref_flat)
        
        # Find peaks above threshold with statistical testing
        threshold = baseline_mean + 2 * baseline_std  # 2 sigma threshold
        peak_indices = np.where(diff_flat > self.enhancer_params['min_accessibility_increase'])[0]
        
        for idx in peak_indices[:10]:  # Limit to top 10 peaks
            # Statistical test for significance
            local_window = 100  # 100bp window
            start_idx = max(0, idx - local_window)
            end_idx = min(len(ref_flat), idx + local_window)
            
            ref_local = ref_flat[start_idx:end_idx]
            alt_local = alt_flat[start_idx:end_idx]
            
            # Perform t-test
            if len(ref_local) > 1 and len(alt_local) > 1:
                t_stat, p_value = stats.ttest_ind(alt_local, ref_local)
                
                if p_value < self.enhancer_params['statistical_significance']:
                    significant_peaks.append({
                        'position': 25332748 + idx,  # Genomic position
                        'ref_value': float(ref_flat[idx]),
                        'alt_value': float(alt_flat[idx]),
                        'diff_value': float(diff_flat[idx]),
                        'p_value': p_value,
                        't_statistic': t_stat
                    })
        
        return significant_peaks
    
    def _calculate_enhancer_score(self, peak: Dict[str, Any],
                                 histone_analysis: Dict[str, Any],
                                 rna_analysis: Dict[str, Any]) -> float:
        """Calculate composite enhancer score based on multiple evidence types"""
        score = 0.0
        max_score = 0.0
        
        # DNase accessibility contribution (40% weight)
        dnase_score = min(peak['diff_value'] / 0.5, 1.0) * 0.4
        score += dnase_score
        max_score += 0.4
        
        # Statistical significance contribution (20% weight)
        if peak['p_value'] < 0.001:
            stat_score = 0.2
        elif peak['p_value'] < 0.01:
            stat_score = 0.15
        elif peak['p_value'] < 0.05:
            stat_score = 0.1
        else:
            stat_score = 0.0
        score += stat_score
        max_score += 0.2
        
        # Histone modification contribution (30% weight)
        if histone_analysis and not histone_analysis.get('error'):
            enhancer_signatures = histone_analysis.get('enhancer_signatures', [])
            if enhancer_signatures:
                histone_score = 0.0
                for sig in enhancer_signatures:
                    if sig.get('potentially_enhancer_creating', False):
                        histone_score = max(histone_score, 0.3)
                        break
                score += histone_score
        max_score += 0.3
        
        # RNA expression contribution (10% weight)
        if rna_analysis and not rna_analysis.get('error'):
            if rna_analysis.get('potential_enhancer_activity', False):
                score += 0.1
        max_score += 0.1
        
        # Normalize score to 0-1 range
        return score / max_score if max_score > 0 else 0.0
    
    def _determine_confidence(self, enhancer_score: float) -> str:
        """Determine confidence level based on enhancer score"""
        if enhancer_score >= self.enhancer_params['confidence_levels']['high']['min_score']:
            return 'high'
        elif enhancer_score >= self.enhancer_params['confidence_levels']['moderate']['min_score']:
            return 'moderate'
        else:
            return 'low'
    
    def _summarize_evidence(self, peak: Dict[str, Any],
                          histone_analysis: Dict[str, Any],
                          rna_analysis: Dict[str, Any]) -> str:
        """Summarize evidence for enhancer detection"""
        evidence_parts = []
        
        # DNase evidence
        evidence_parts.append(f"DNase increase: {peak['diff_value']:.3f} (p={peak['p_value']:.3e})")
        
        # Histone evidence
        if histone_analysis and not histone_analysis.get('error'):
            enhancer_signatures = histone_analysis.get('enhancer_signatures', [])
            for sig in enhancer_signatures:
                if sig.get('potentially_enhancer_creating', False):
                    evidence_parts.append(f"{sig['mark']} change: {sig['mean_change']:.2f}")
        
        # RNA evidence
        if rna_analysis and not rna_analysis.get('error'):
            if rna_analysis.get('potential_enhancer_activity', False):
                expr_change = rna_analysis.get('expression_changes', {}).get('max_increase', 0)
                evidence_parts.append(f"RNA increase: {expr_change:.3e}")
        
        return "; ".join(evidence_parts)
    
    def _perform_statistical_analysis(self, all_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform statistical analysis across all mutation results"""
        successful_results = [r for r in all_results if r.get('status') == 'success']
        
        if not successful_results:
            return {
                'overall_confidence': 'N/A',
                'statistical_summary': 'No successful analyses'
            }
        
        # Extract key metrics
        enhancer_counts = [r.get('enhancers_detected', 0) for r in successful_results]
        enhancer_positive_rate = sum(1 for c in enhancer_counts if c > 0) / len(enhancer_counts)
        
        # Statistical tests
        analysis = {
            'total_variants_analyzed': len(successful_results),
            'enhancer_positive_variants': sum(1 for c in enhancer_counts if c > 0),
            'enhancer_positive_rate': enhancer_positive_rate,
            'total_enhancers': sum(enhancer_counts),
            'mean_enhancers_per_variant': np.mean(enhancer_counts),
            'std_enhancers_per_variant': np.std(enhancer_counts),
            'max_enhancers_single_variant': max(enhancer_counts) if enhancer_counts else 0,
            'overall_confidence': 'N/A'
        }
        
        # Determine overall confidence
        if enhancer_positive_rate > 0.5 and analysis['total_enhancers'] > 10:
            analysis['overall_confidence'] = 'HIGH'
        elif enhancer_positive_rate > 0.3 and analysis['total_enhancers'] > 5:
            analysis['overall_confidence'] = 'MODERATE'
        elif analysis['total_enhancers'] > 0:
            analysis['overall_confidence'] = 'LOW'
        else:
            analysis['overall_confidence'] = 'NONE'
        
        # Binomial test for significance
        if analysis['enhancer_positive_variants'] > 0:
            # Test against null hypothesis of random occurrence (p=0.1)
            from scipy.stats import binom_test
            p_value = binom_test(
                analysis['enhancer_positive_variants'],
                analysis['total_variants_analyzed'],
                p=0.1,
                alternative='greater'
            )
            analysis['binomial_test_p_value'] = p_value
            analysis['statistically_significant'] = p_value < 0.05
        
        return analysis
    
    def _detect_enhancer_patterns(self, all_results: List[Dict[str, Any]], 
                                 statistical_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Detect patterns and networks in enhancer creation"""
        patterns = {
            'network_detected': False,
            'network_description': '',
            'hotspot_regions': [],
            'common_features': []
        }
        
        successful_results = [r for r in all_results if r.get('status') == 'success' and r.get('enhancers_detected', 0) > 0]
        
        if not successful_results:
            return patterns
        
        # Collect all enhancer positions
        all_enhancer_positions = []
        for result in successful_results:
            for enhancer in result.get('enhancer_evidence', []):
                if 'genomic_position' in enhancer:
                    all_enhancer_positions.append(enhancer['genomic_position'])
        
        if len(all_enhancer_positions) >= 3:
            # Check for clustering (hotspots)
            positions_array = np.array(all_enhancer_positions)
            
            # Simple clustering: find regions with multiple enhancers within 10kb
            window_size = 10000
            hotspots = []
            
            for pos in np.unique(positions_array):
                nearby = positions_array[np.abs(positions_array - pos) < window_size]
                if len(nearby) >= 2:
                    hotspots.append({
                        'center': int(pos),
                        'enhancer_count': len(nearby),
                        'span': int(np.max(nearby) - np.min(nearby))
                    })
            
            if hotspots:
                patterns['hotspot_regions'] = hotspots[:5]  # Top 5 hotspots
                patterns['network_detected'] = True
                patterns['network_description'] = f"Found {len(hotspots)} enhancer hotspot regions"
        
        # Analyze common features
        if statistical_analysis.get('enhancer_positive_rate', 0) > 0.3:
            patterns['common_features'].append('High mutation-to-enhancer conversion rate')
        
        if statistical_analysis.get('statistically_significant', False):
            patterns['common_features'].append('Statistically significant enhancer creation')
        
        return patterns
    
    def _generate_comprehensive_report(self, mutation_data: Dict[str, Any],
                                      all_results: List[Dict[str, Any]],
                                      statistical_analysis: Dict[str, Any],
                                      enhancer_patterns: Dict[str, Any],
                                      research_question: str) -> Dict[str, Any]:
        """Generate comprehensive multi-mutation analysis report"""
        gene = mutation_data.get('gene', 'Unknown')
        cancer_type = mutation_data.get('cancer_type', 'Unknown')
        
        # Create detailed report content
        report_content = f"""# Multi-Mutation Enhancer Analysis Report

## Research Question
{research_question}

## Executive Summary
- **Gene**: {gene}
- **Cancer Type**: {cancer_type}
- **Total Mutations Analyzed**: {statistical_analysis['total_variants_analyzed']}
- **Enhancer-Positive Variants**: {statistical_analysis['enhancer_positive_variants']} ({statistical_analysis['enhancer_positive_rate']:.1%})
- **Total Enhancers Detected**: {statistical_analysis['total_enhancers']}
- **Statistical Confidence**: {statistical_analysis['overall_confidence']}
- **Network Detection**: {'YES' if enhancer_patterns['network_detected'] else 'NO'}

## Statistical Analysis
- **Mean Enhancers per Variant**: {statistical_analysis['mean_enhancers_per_variant']:.2f} ± {statistical_analysis['std_enhancers_per_variant']:.2f}
- **Maximum Enhancers (single variant)**: {statistical_analysis['max_enhancers_single_variant']}
"""
        
        if 'binomial_test_p_value' in statistical_analysis:
            report_content += f"- **Binomial Test p-value**: {statistical_analysis['binomial_test_p_value']:.3e}\n"
            report_content += f"- **Statistically Significant**: {'YES' if statistical_analysis['statistically_significant'] else 'NO'}\n"
        
        # Add pattern analysis
        if enhancer_patterns['network_detected']:
            report_content += f"\n## Enhancer Network Analysis\n"
            report_content += f"**Network Status**: {enhancer_patterns['network_description']}\n\n"
            
            if enhancer_patterns['hotspot_regions']:
                report_content += "### Hotspot Regions\n"
                for i, hotspot in enumerate(enhancer_patterns['hotspot_regions'], 1):
                    report_content += f"{i}. Position {hotspot['center']:,}: {hotspot['enhancer_count']} enhancers within {hotspot['span']}bp\n"
        
        # Add detailed results for each variant
        report_content += "\n## Detailed Variant Analysis\n"
        successful_results = [r for r in all_results if r.get('status') == 'success']
        
        for result in successful_results[:10]:  # Show top 10
            variant_id = result.get('variant_id', 'Unknown')
            enhancers = result.get('enhancers_detected', 0)
            report_content += f"\n### {variant_id}\n"
            report_content += f"- Enhancers Detected: {enhancers}\n"
            
            if enhancers > 0 and 'enhancer_evidence' in result:
                for enhancer in result['enhancer_evidence'][:3]:  # Show top 3 enhancers
                    report_content += f"  - Position {enhancer.get('genomic_position', 'N/A')}: "
                    report_content += f"Score={enhancer.get('enhancer_score', 0):.2f}, "
                    report_content += f"Confidence={enhancer.get('confidence', 'N/A')}\n"
        
        # Save report
        report_file = f"reports/multi_mutation/{gene}_{cancer_type}_multi_analysis_{self.timestamp}.md"
        with open(report_file, 'w') as f:
            f.write(report_content)
        
        print(f"   📄 Report saved: {report_file}")
        
        return {'report_file': report_file, 'content': report_content}
    
    def _create_advanced_visualizations(self, all_results: List[Dict[str, Any]],
                                       statistical_analysis: Dict[str, Any],
                                       enhancer_patterns: Dict[str, Any],
                                       gene: str, cancer_type: str) -> List[str]:
        """Create advanced visualizations for multi-mutation analysis"""
        viz_files = []
        
        # 1. Enhancer distribution heatmap
        viz_file = self._create_enhancer_heatmap(all_results, gene, cancer_type)
        if viz_file:
            viz_files.append(viz_file)
        
        # 2. Statistical summary plot
        viz_file = self._create_statistical_summary(statistical_analysis, gene, cancer_type)
        if viz_file:
            viz_files.append(viz_file)
        
        # 3. Network visualization (if detected)
        if enhancer_patterns['network_detected']:
            viz_file = self._create_network_visualization(enhancer_patterns, gene, cancer_type)
            if viz_file:
                viz_files.append(viz_file)
        
        return viz_files
    
    def _create_enhancer_heatmap(self, all_results: List[Dict[str, Any]], 
                                 gene: str, cancer_type: str) -> Optional[str]:
        """Create heatmap of enhancer distribution across variants"""
        try:
            successful_results = [r for r in all_results if r.get('status') == 'success']
            
            if not successful_results:
                return None
            
            # Prepare data for heatmap
            variant_ids = []
            enhancer_data = []
            
            for result in successful_results[:20]:  # Limit to 20 for visibility
                variant_id = result.get('variant_id', 'Unknown').split('_')[1] if '_' in result.get('variant_id', '') else result.get('variant_id', 'Unknown')
                variant_ids.append(variant_id)
                enhancer_data.append(result.get('enhancers_detected', 0))
            
            # Create figure
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Create bar plot
            colors = ['red' if x > 0 else 'gray' for x in enhancer_data]
            bars = ax.bar(range(len(variant_ids)), enhancer_data, color=colors, alpha=0.7)
            
            # Customize plot
            ax.set_xlabel('Variant', fontsize=12)
            ax.set_ylabel('Number of Enhancers Detected', fontsize=12)
            ax.set_title(f'Enhancer Distribution Across {gene} Variants in {cancer_type.title()} Cancer', 
                        fontsize=14, fontweight='bold')
            ax.set_xticks(range(len(variant_ids)))
            ax.set_xticklabels(variant_ids, rotation=45, ha='right')
            
            # Add value labels on bars
            for bar, value in zip(bars, enhancer_data):
                if value > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.1,
                           str(int(value)), ha='center', va='bottom', fontweight='bold')
            
            # Add grid
            ax.grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            filename = f"visualizations/multi_mutation/{gene}_{cancer_type}_enhancer_distribution_{self.timestamp}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            return filename
            
        except Exception as e:
            print(f"   ⚠️ Error creating heatmap: {e}")
            return None
    
    def _create_statistical_summary(self, statistical_analysis: Dict[str, Any],
                                   gene: str, cancer_type: str) -> Optional[str]:
        """Create statistical summary visualization"""
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
            
            # 1. Pie chart of enhancer-positive vs negative variants
            labels = ['Enhancer-positive', 'No enhancers']
            sizes = [
                statistical_analysis['enhancer_positive_variants'],
                statistical_analysis['total_variants_analyzed'] - statistical_analysis['enhancer_positive_variants']
            ]
            colors = ['#2ecc71', '#e74c3c']
            ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax1.set_title('Variant Classification', fontweight='bold')
            
            # 2. Bar chart of key statistics
            metrics = ['Total\nVariants', 'Enhancer\nPositive', 'Total\nEnhancers']
            values = [
                statistical_analysis['total_variants_analyzed'],
                statistical_analysis['enhancer_positive_variants'],
                statistical_analysis['total_enhancers']
            ]
            ax2.bar(metrics, values, color=['#3498db', '#2ecc71', '#9b59b6'], alpha=0.7)
            ax2.set_title('Analysis Summary', fontweight='bold')
            ax2.set_ylabel('Count')
            
            # Add value labels
            for i, (metric, value) in enumerate(zip(metrics, values)):
                ax2.text(i, value + max(values)*0.02, str(int(value)), 
                        ha='center', va='bottom', fontweight='bold')
            
            # 3. Distribution statistics
            stats_text = f"""Statistical Summary
            
Mean enhancers/variant: {statistical_analysis['mean_enhancers_per_variant']:.2f}
Std deviation: {statistical_analysis['std_enhancers_per_variant']:.2f}
Max enhancers: {statistical_analysis['max_enhancers_single_variant']}
Positive rate: {statistical_analysis['enhancer_positive_rate']:.1%}

Overall Confidence: {statistical_analysis['overall_confidence']}"""
            
            if 'binomial_test_p_value' in statistical_analysis:
                stats_text += f"\n\nBinomial test p-value: {statistical_analysis['binomial_test_p_value']:.3e}"
                stats_text += f"\nStatistically significant: {'YES' if statistical_analysis['statistically_significant'] else 'NO'}"
            
            ax3.text(0.1, 0.9, stats_text, transform=ax3.transAxes, fontsize=11,
                    verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            ax3.set_xlim(0, 1)
            ax3.set_ylim(0, 1)
            ax3.axis('off')
            
            # 4. Confidence gauge
            confidence_levels = ['NONE', 'LOW', 'MODERATE', 'HIGH']
            confidence_colors = ['#e74c3c', '#f39c12', '#f1c40f', '#2ecc71']
            current_confidence = statistical_analysis['overall_confidence']
            
            if current_confidence in confidence_levels:
                conf_index = confidence_levels.index(current_confidence)
                ax4.barh(range(len(confidence_levels)), [1]*len(confidence_levels), 
                        color=confidence_colors, alpha=0.3)
                ax4.barh(conf_index, 1, color=confidence_colors[conf_index], alpha=1.0)
                ax4.set_yticks(range(len(confidence_levels)))
                ax4.set_yticklabels(confidence_levels)
                ax4.set_xlim(0, 1)
                ax4.set_xticks([])
                ax4.set_title('Analysis Confidence Level', fontweight='bold')
                ax4.text(0.5, conf_index, '◄ Current', ha='center', va='center', 
                        fontweight='bold', fontsize=12)
            
            plt.suptitle(f'{gene} Multi-Mutation Analysis - {cancer_type.title()} Cancer', 
                        fontsize=16, fontweight='bold')
            plt.tight_layout()
            
            filename = f"visualizations/multi_mutation/{gene}_{cancer_type}_statistical_summary_{self.timestamp}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            return filename
            
        except Exception as e:
            print(f"   ⚠️ Error creating statistical summary: {e}")
            return None
    
    def _create_network_visualization(self, enhancer_patterns: Dict[str, Any],
                                     gene: str, cancer_type: str) -> Optional[str]:
        """Create network visualization of enhancer hotspots"""
        try:
            if not enhancer_patterns.get('hotspot_regions'):
                return None
            
            fig, ax = plt.subplots(figsize=(14, 6))
            
            # Plot hotspot regions
            hotspots = enhancer_patterns['hotspot_regions']
            
            # Create a genomic track visualization
            for i, hotspot in enumerate(hotspots):
                center = hotspot['center']
                span = hotspot['span']
                count = hotspot['enhancer_count']
                
                # Draw hotspot region
                rect = plt.Rectangle((center - span/2, i), span, 0.8, 
                                    facecolor='red', alpha=0.3 + 0.1*count, 
                                    edgecolor='darkred', linewidth=2)
                ax.add_patch(rect)
                
                # Add label
                ax.text(center, i + 0.4, f'{count} enhancers\n{span}bp', 
                       ha='center', va='center', fontweight='bold', fontsize=10)
            
            # Set axis properties
            ax.set_ylim(-0.5, len(hotspots))
            ax.set_xlabel('Genomic Position', fontsize=12)
            ax.set_ylabel('Hotspot Regions', fontsize=12)
            ax.set_title(f'Enhancer Network Hotspots - {gene} in {cancer_type.title()} Cancer', 
                        fontsize=14, fontweight='bold')
            
            # Format x-axis
            ax.ticklabel_format(style='plain', axis='x')
            ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
            
            # Add grid
            ax.grid(True, alpha=0.3, axis='x')
            
            # Remove y-axis ticks
            ax.set_yticks(range(len(hotspots)))
            ax.set_yticklabels([f'Hotspot {i+1}' for i in range(len(hotspots))])
            
            plt.tight_layout()
            filename = f"visualizations/multi_mutation/{gene}_{cancer_type}_network_hotspots_{self.timestamp}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            return filename
            
        except Exception as e:
            print(f"   ⚠️ Error creating network visualization: {e}")
            return None
    
    def _save_analysis_data(self, mutation_data: Dict[str, Any],
                           all_results: List[Dict[str, Any]],
                           statistical_analysis: Dict[str, Any],
                           enhancer_patterns: Dict[str, Any],
                           gene: str, cancer_type: str):
        """Save all analysis data for reproducibility"""
        data_file = f"data/multi_mutation/{gene}_{cancer_type}_analysis_{self.timestamp}.json"
        
        # Prepare data for JSON serialization
        save_data = {
            'timestamp': self.timestamp,
            'gene': gene,
            'cancer_type': cancer_type,
            'mutation_data': mutation_data,
            'analysis_results_summary': {
                'total_results': len(all_results),
                'successful': len([r for r in all_results if r.get('status') == 'success']),
                'failed': len([r for r in all_results if r.get('status') == 'error'])
            },
            'statistical_analysis': statistical_analysis,
            'enhancer_patterns': enhancer_patterns
        }
        
        # Save without the actual numpy arrays (too large)
        with open(data_file, 'w') as f:
            json.dump(save_data, f, indent=2, default=str)
        
        print(f"   💾 Analysis data saved: {data_file}")


def main():
    """Main pipeline execution"""
    parser = argparse.ArgumentParser(
        description="Multi-Mutation Enhancer Detection Pipeline - Advanced Statistical Analysis"
    )
    parser.add_argument('--gene', required=True, 
                       help='Gene to analyze (e.g., KRAS, PIK3CA, TP53)')
    parser.add_argument('--cancer', required=True,
                       choices=['breast', 'pancreatic', 'lung_adenocarcinoma', 
                               'glioblastoma', 'colorectal', 'prostate'],
                       help='Cancer type to analyze')
    parser.add_argument('--max-mutations', type=int, default=50,
                       help='Maximum number of mutations to analyze (default: 50)')
    parser.add_argument('--batch-size', type=int, default=5,
                       help='Number of parallel API calls (default: 5)')
    
    args = parser.parse_args()
    
    # Get AlphaGenome API key
    api_key = os.environ.get('ALPHAGENOME_API_KEY')
    if not api_key:
        print("❌ ERROR: ALPHAGENOME_API_KEY environment variable not set")
        print("Set it with: export ALPHAGENOME_API_KEY='your_key_here'")
        return 1
    
    try:
        # Initialize pipeline
        pipeline = MultiMutationEnhancerPipeline(api_key)
        
        # Run analysis
        result = pipeline.analyze_multiple_mutations(
            args.gene, args.cancer, args.max_mutations, args.batch_size
        )
        
        if result['status'] == 'success':
            return 0
        else:
            print(f"\n❌ ANALYSIS FAILED: {result.get('error', 'Unknown error')}")
            return 1
            
    except Exception as e:
        print(f"\n❌ PIPELINE ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())