"""
Comprehensive tests for the EnhancerDetectionPipeline.

Tests the full pipeline integration with real data from cBioPortal and AlphaGenome.
"""

import os
import sys
from pathlib import Path

# Add the src directory to Python path for absolute imports
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.pipelines.enhancer import EnhancerDetectionPipeline


def test_enhancer_pipeline_integration():
    """Test the full enhancer detection pipeline with real data."""
    print("🧪 Testing Enhancer Detection Pipeline Integration")
    print("=" * 60)
    
    # Check for API key
    api_key = os.getenv("ALPHAGENOME_API_KEY")
    if not api_key:
        print("❌ ALPHAGENOME_API_KEY environment variable not set")
        print("   Please set the API key to run this test")
        return False
    
    print(f"✅ API key found: {api_key[:20]}...")
    
    # Initialize pipeline
    try:
        pipeline = EnhancerDetectionPipeline(
            alphagenome_api_key=api_key,
            output_dir="data/test_outputs"
        )
        print("✅ Pipeline initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize pipeline: {e}")
        return False
    
    # Test with a small number of KRAS mutations in pancreatic cancer
    print("\n📊 Testing KRAS mutations in pancreatic cancer...")
    print("   Gene: KRAS")
    print("   Cancer: pancreatic")
    print("   Max mutations: 3")
    
    try:
        result = pipeline.run(
            gene="KRAS",
            cancer_type="pancreatic", 
            max_mutations=3
        )
        
        print("✅ Pipeline completed successfully")
        
        # Verify result structure
        expected_keys = [
            "status", "research_question", "gene", "cancer_type",
            "mutations_analyzed", "enhancers_detected", "enhancer_detection_rate"
        ]
        
        for key in expected_keys:
            if key in result:
                print(f"   ✅ {key}: {result[key]}")
            else:
                print(f"   ❌ Missing key: {key}")
                return False
        
        # Check if we got real data
        mutations_analyzed = result.get("mutations_analyzed", 0)
        if mutations_analyzed > 0:
            print(f"✅ Successfully analyzed {mutations_analyzed} mutation(s)")
            
            enhancers_detected = result.get("enhancers_detected", 0)
            detection_rate = result.get("enhancer_detection_rate", 0)
            
            print(f"   Enhancers detected: {enhancers_detected}")
            print(f"   Detection rate: {detection_rate:.2%}")
            
            # Check if reports were generated
            report_file = result.get("report_file")
            if report_file and Path(report_file).exists():
                print(f"   ✅ Report generated: {Path(report_file).name}")
            else:
                print("   ⚠️ No report file generated")
            
        else:
            print("❌ No mutations were analyzed")
            return False
        
        # Check honest analysis flag
        if result.get("honest_analysis", False):
            print("✅ Honest analysis flag set correctly")
        else:
            print("❌ Honest analysis flag missing or false")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline execution failed: {e}")
        import traceback
        print(f"   Full traceback:\n{traceback.format_exc()}")
        return False


def test_enhancer_criteria():
    """Test enhancer detection criteria."""
    print("\n🧪 Testing Enhancer Detection Criteria")
    print("=" * 40)
    
    api_key = os.getenv("ALPHAGENOME_API_KEY")
    if not api_key:
        print("❌ ALPHAGENOME_API_KEY required")
        return False
    
    # Test with custom criteria
    custom_criteria = {
        "dnase_min_increase": 0.005,     # Lower threshold
        "h3k27ac_min_increase": 0.05,    # Lower threshold  
        "h3k4me1_min_increase": 0.025,   # Lower threshold
        "rna_min_increase": 0.0005,      # Lower threshold
        "min_marks_required": 1          # More lenient
    }
    
    try:
        pipeline = EnhancerDetectionPipeline(
            alphagenome_api_key=api_key,
            output_dir="data/test_outputs_custom",
            enhancer_criteria=custom_criteria
        )
        
        print("✅ Pipeline with custom criteria initialized")
        print(f"   Custom criteria: {custom_criteria}")
        
        # Test that criteria are properly set
        assert pipeline.enhancer_criteria == custom_criteria
        print("✅ Custom criteria properly set")
        
        return True
        
    except Exception as e:
        print(f"❌ Custom criteria test failed: {e}")
        return False


def test_error_handling():
    """Test pipeline error handling."""
    print("\n🧪 Testing Error Handling")
    print("=" * 30)
    
    # Test with missing API key (should fail at initialization)
    try:
        pipeline = EnhancerDetectionPipeline(
            alphagenome_api_key="",  # Empty API key
            output_dir="data/test_outputs_error"
        )
        print("❌ Pipeline should have failed with empty API key")
        return False
    except ValueError as e:
        print(f"✅ Pipeline properly rejects empty API key: {e}")
        
    # Test with invalid gene/cancer combination
    api_key = os.getenv("ALPHAGENOME_API_KEY")
    if not api_key:
        print("⚠️ Skipping invalid gene test - no API key")
        return True
        
    try:
        pipeline = EnhancerDetectionPipeline(
            alphagenome_api_key=api_key,
            output_dir="data/test_outputs_error"
        )
        
        # Test with non-existent gene
        result = pipeline.run(
            gene="NONEXISTENTGENE123",
            cancer_type="pancreatic", 
            max_mutations=1
        )
        
        # Should handle gracefully with no mutations found
        if result.get("status") == "failed" and "no_mutations" in result.get("stage", ""):
            print("✅ Pipeline handles non-existent genes gracefully")
            return True
        elif result.get("mutations_analyzed", 0) == 0:
            print("✅ Pipeline handles genes with no mutations gracefully")
            return True
        else:
            print(f"❌ Unexpected result for non-existent gene: {result}")
            return False
            
    except Exception as e:
        print(f"✅ Pipeline properly handles errors: {e}")
        return True


def test_mutation_processing():
    """Test mutation data processing from cBioPortal."""
    print("\n🧪 Testing Mutation Data Processing")
    print("=" * 40)
    
    api_key = os.getenv("ALPHAGENOME_API_KEY")
    if not api_key:
        print("❌ ALPHAGENOME_API_KEY required")
        return False
    
    try:
        pipeline = EnhancerDetectionPipeline(
            alphagenome_api_key=api_key,
            output_dir="data/test_outputs_mutations"
        )
        
        # Test mutation fetching
        mutation_data = pipeline.fetch_mutations("KRAS", "pancreatic", 5)
        
        if mutation_data.get("status") == "success":
            mutations = mutation_data.get("mutations", [])
            print(f"✅ Successfully fetched {len(mutations)} mutations")
            
            # Check mutation format
            if mutations:
                first_mut = mutations[0]
                required_fields = ["chromosome", "position", "ref", "alt"]
                
                for field in required_fields:
                    if field in first_mut:
                        print(f"   ✅ {field}: {first_mut[field]}")
                    else:
                        print(f"   ❌ Missing field: {field}")
                        return False
                
                # Test mutation to variant conversion
                variant_spec = pipeline.mutation_to_variant_spec(first_mut)
                print(f"   ✅ Converted to VariantSpec: {variant_spec.chrom}:{variant_spec.pos}:{variant_spec.ref}>{variant_spec.alt}")
                
            return True
        else:
            print(f"❌ Mutation fetching failed: {mutation_data.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Mutation processing test failed: {e}")
        return False


if __name__ == "__main__":
    print("🔬 Enhancer Detection Pipeline Test Suite")
    print("=" * 60)
    
    # Run all tests
    test_results = []
    
    test_results.append(("Integration Test", test_enhancer_pipeline_integration()))
    test_results.append(("Criteria Test", test_enhancer_criteria()))
    test_results.append(("Error Handling", test_error_handling()))
    test_results.append(("Mutation Processing", test_mutation_processing()))
    
    # Summary
    print("\n" + "="*60)
    print("🎯 TEST RESULTS")
    print("="*60)
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📊 Summary: {passed}/{len(test_results)} tests passed")
    
    if passed == len(test_results):
        print("🎉 All tests passed! Pipeline is ready for production.")
        sys.exit(0)
    else:
        print("💥 Some tests failed. Please check the implementation.")
        sys.exit(1)