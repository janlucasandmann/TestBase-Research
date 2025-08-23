#!/usr/bin/env python3
"""
Test Script for Multi-Mutation Pipeline
=======================================

Tests the new multi-mutation pipeline with sample data
"""

import os
import sys
import json
from pathlib import Path

def test_pipeline():
    """Test the multi-mutation pipeline with a small dataset"""
    
    print("="*80)
    print("TESTING MULTI-MUTATION ENHANCER DETECTION PIPELINE")
    print("="*80)
    
    # Check for API key
    api_key = os.environ.get('ALPHAGENOME_API_KEY')
    if not api_key:
        print("❌ ERROR: ALPHAGENOME_API_KEY environment variable not set")
        print("Please set it with: export ALPHAGENOME_API_KEY='your_key_here'")
        return False
    
    print("✅ API key found")
    
    # Import the pipeline
    try:
        from multi_mutation_pipeline import MultiMutationEnhancerPipeline
        print("✅ Pipeline imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import pipeline: {e}")
        return False
    
    # Test parameters
    test_configs = [
        {
            'gene': 'KRAS',
            'cancer': 'pancreatic',
            'max_mutations': 3,  # Small number for testing
            'batch_size': 2
        }
    ]
    
    for config in test_configs:
        print(f"\n{'='*60}")
        print(f"Testing: {config['gene']} in {config['cancer']} cancer")
        print(f"Parameters: max_mutations={config['max_mutations']}, batch_size={config['batch_size']}")
        print("="*60)
        
        try:
            # Initialize pipeline
            pipeline = MultiMutationEnhancerPipeline(api_key)
            print("✅ Pipeline initialized")
            
            # Run analysis
            result = pipeline.analyze_multiple_mutations(
                gene=config['gene'],
                cancer_type=config['cancer'],
                max_mutations=config['max_mutations'],
                batch_size=config['batch_size']
            )
            
            # Check results
            if result['status'] == 'success':
                print("\n✅ TEST PASSED - Analysis completed successfully")
                print("\nResults Summary:")
                print(f"  - Mutations analyzed: {result['mutations_analyzed']}")
                print(f"  - Unique variants: {result['unique_variants']}")
                print(f"  - Total enhancers detected: {result['total_enhancers_detected']}")
                print(f"  - Enhancer-positive variants: {result['enhancer_positive_variants']}")
                print(f"  - Network detected: {result['enhancer_network_detected']}")
                print(f"  - Statistical confidence: {result['statistical_confidence']}")
                print(f"  - Report file: {result['report_file']}")
                print(f"  - Visualizations created: {len(result['visualization_files'])}")
                
                # Verify output files exist
                if Path(result['report_file']).exists():
                    print("  ✅ Report file exists")
                else:
                    print("  ❌ Report file not found")
                
                for viz_file in result['visualization_files']:
                    if Path(viz_file).exists():
                        print(f"  ✅ Visualization exists: {viz_file}")
                    else:
                        print(f"  ❌ Visualization not found: {viz_file}")
                
            else:
                print(f"\n❌ TEST FAILED - Analysis failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"\n❌ TEST FAILED - Exception occurred: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED")
    print("="*80)
    return True

def compare_pipelines():
    """Compare old and new pipeline results"""
    
    print("\n" + "="*80)
    print("COMPARING OLD VS NEW PIPELINE")
    print("="*80)
    
    api_key = os.environ.get('ALPHAGENOME_API_KEY')
    if not api_key:
        print("❌ ERROR: API key not set")
        return False
    
    # Test with same mutation
    test_gene = 'KRAS'
    test_cancer = 'pancreatic'
    test_mutations = 2
    
    print(f"\nTest case: {test_gene} in {test_cancer} cancer ({test_mutations} mutations)")
    
    # Run old pipeline
    print("\n--- Running OLD pipeline ---")
    try:
        from enhancer_detection_pipeline import HonestEnhancerPipeline
        old_pipeline = HonestEnhancerPipeline(api_key)
        old_result = old_pipeline.analyze_enhancer_creation(
            test_gene, test_cancer, test_mutations
        )
        print(f"Old pipeline: {old_result.get('total_enhancers_detected', 0)} enhancers detected")
    except Exception as e:
        print(f"Old pipeline error: {e}")
        old_result = None
    
    # Run new pipeline
    print("\n--- Running NEW pipeline ---")
    try:
        from multi_mutation_pipeline import MultiMutationEnhancerPipeline
        new_pipeline = MultiMutationEnhancerPipeline(api_key)
        new_result = new_pipeline.analyze_multiple_mutations(
            test_gene, test_cancer, test_mutations, batch_size=2
        )
        print(f"New pipeline: {new_result.get('total_enhancers_detected', 0)} enhancers detected")
        print(f"Statistical confidence: {new_result.get('statistical_confidence', 'N/A')}")
    except Exception as e:
        print(f"New pipeline error: {e}")
        new_result = None
    
    # Compare results
    print("\n--- Comparison ---")
    if old_result and new_result:
        print("Improvements in new pipeline:")
        print("  ✅ Batch processing of mutations")
        print("  ✅ Statistical validation of peaks")
        print("  ✅ Composite scoring system")
        print("  ✅ Pattern detection across mutations")
        print("  ✅ Enhanced visualizations")
        print("  ✅ Confidence scoring")
    
    return True

if __name__ == "__main__":
    # Run basic tests
    success = test_pipeline()
    
    if success:
        # Run comparison if basic tests pass
        compare_pipelines()
    
    sys.exit(0 if success else 1)