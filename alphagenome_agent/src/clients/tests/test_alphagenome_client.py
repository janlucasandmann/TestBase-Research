"""Test script for AlphaGenomeClient - verifies real API integration works correctly."""

import os
import sys
from pathlib import Path

# Add the src directory to Python path for absolute imports
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.clients.alphagenome_client import AlphaGenomeClient, VariantSpec

def test_alphagenome_client():
    """Test the AlphaGenomeClient with real API calls."""
    print("🧪 Testing AlphaGenome Client")
    print("=" * 50)
    
    # Check for API key
    api_key = os.getenv("ALPHAGENOME_API_KEY")
    if not api_key:
        print("❌ ALPHAGENOME_API_KEY environment variable not set")
        print("   Please set the API key to run this test")
        return False
    
    print(f"✅ API key found: {api_key[:20]}...")
    
    # Initialize client
    try:
        client = AlphaGenomeClient(api_key=api_key)
        print("✅ Client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        return False
    
    # Test with KRAS variant (known to work)
    print("\n📊 Testing KRAS G12V variant analysis...")
    
    # Use AlphaGenomeClient's VariantSpec
    variant = VariantSpec(
        chrom="chr12",
        pos=25398284,
        ref="C",
        alt="A"
    )
    
    # AlphaGenomeClient expects interval_bp as integer (window size)
    # Must be one of: [2048, 16384, 131072, 524288, 1048576]
    interval_bp = 16384  # 16kb window around variant
    
    print(f"   Variant: {variant.chrom}:{variant.pos}:{variant.ref}>{variant.alt}")
    print(f"   Window size: {interval_bp}bp")
    print(f"   Tissue: pancreatic")
    
    # Run analysis
    try:
        result = client.predict_variant_effects(variant, interval_bp, tissue="pancreatic")
        print("✅ Analysis completed successfully")
        
        # Check result structure
        expected_keys = ["variant", "interval_bp", "tissue_terms", "summary", "raw"]
        for key in expected_keys:
            if key in result:
                print(f"   ✅ {key}: present")
            else:
                print(f"   ❌ Missing key: {key}")
                return False
        
        # Check summary results
        summary = result.get("summary", {})
        print(f"\n📈 Analysis Results:")
        print(f"   Variant: {result.get('variant', 'Unknown')}")
        print(f"   Window: {result.get('interval_bp', 0)}bp")
        print(f"   Tissue: {result.get('tissue_terms', [])}")
        
        # Check DNase results
        if "dnase" in summary:
            dnase = summary["dnase"]
            print(f"\n   DNase Accessibility:")
            print(f"     Reference mean: {dnase.get('ref_mean', 0):.4f}")
            print(f"     Alternate mean: {dnase.get('alt_mean', 0):.4f}")
            print(f"     Max increase: {dnase.get('max_increase', 0):.4f}")
            if dnase.get('max_increase', 0) > 0:
                print("     ✅ DNase increase detected")
        
        # Check RNA-seq results
        if "rna_seq" in summary:
            rna = summary["rna_seq"]
            print(f"\n   RNA Expression:")
            print(f"     Reference mean: {rna.get('ref_mean', 0):.4f}")
            print(f"     Alternate mean: {rna.get('alt_mean', 0):.4f}")
            print(f"     Max increase: {rna.get('max_increase', 0):.4f}")
            if rna.get('max_increase', 0) > 0:
                print("     ✅ RNA increase detected")
        
        # Check histone marks
        if "chip_histone" in summary:
            histone = summary["chip_histone"]
            marks = histone.get("marks", {})
            print(f"\n   Histone Marks:")
            for mark_name, values in marks.items():
                print(f"     {mark_name}:")
                print(f"       Reference mean: {values.get('ref_mean', 0):.4f}")
                print(f"       Alternate mean: {values.get('alt_mean', 0):.4f}")
                print(f"       Max increase: {values.get('max_increase', 0):.4f}")
                if values.get('max_increase', 0) > 0:
                    print(f"       ✅ {mark_name} increase detected")
        
        # Check raw outputs exist
        raw = result.get("raw", {})
        if raw:
            print(f"\n   Raw Data:")
            print(f"     Reference outputs: {'✅' if 'reference' in raw else '❌'}")
            print(f"     Alternate outputs: {'✅' if 'alternate' in raw else '❌'}")
        
        print(f"\n🎯 Test Summary:")
        print(f"   API call successful: ✅")
        print(f"   Data returned: {'yes' if summary else 'no'}")
        print(f"   Tissue-specific: {'yes' if result.get('tissue_terms') else 'no'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        print(f"   Full traceback:\n{traceback.format_exc()}")
        return False


def test_alphagenome_client_error_handling():
    """Test AlphaGenomeClient error handling."""
    print("\n🧪 Testing Error Handling")
    print("=" * 30)
    
    # Test without API key
    print("Testing without API key...")
    try:
        client = AlphaGenomeClient(api_key=None)
        print("❌ Should have raised error for missing API key")
        return False
    except ValueError as e:
        print(f"✅ Proper error handling: {e}")
        return True
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    if "error" in result:
        print(f"✅ Proper error handling: {result['error']}")
        return True
    else:
        print("❌ Should have returned error without API key")
        return False


if __name__ == "__main__":
    print("🔬 AlphaGenome Client Test Suite")
    print("=" * 50)
    
    # Test 1: Basic functionality
    success1 = test_alphagenome_client()
    
    # Test 2: Error handling  
    success2 = test_alphagenome_client_error_handling()
    
    # Summary
    print(f"\n🎯 Test Results:")
    print(f"   Basic functionality: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"   Error handling: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 and success2:
        print(f"\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print(f"\n💥 Some tests failed!")
        sys.exit(1)