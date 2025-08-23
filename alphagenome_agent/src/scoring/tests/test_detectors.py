"""
Tests for professional detection modules.
"""

import os
import sys
from pathlib import Path

# Add the src directory to Python path for absolute imports
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.scoring.detectors import (
    DetectorFactory, DetectionAlgorithm, ConfidenceLevel,
    EnhancerDetector, PromoterDetector
)


def test_enhancer_detector_algorithms():
    """Test different enhancer detection algorithms."""
    print("🧪 Testing Enhancer Detection Algorithms")
    print("=" * 50)
    
    # Mock AlphaGenome summary with strong enhancer signals
    strong_enhancer_summary = {
        "dnase": {"max_increase": 0.15},  # Strong DNase signal
        "chip_histone": {
            "marks": {
                "H3K27ac": {"max_increase": 0.25},  # Strong active enhancer
                "H3K4me1": {"max_increase": 0.12},  # Strong enhancer mark
                "H3K4me3": {"max_increase": 0.02}   # Low promoter mark (good for enhancer)
            }
        },
        "rna_seq": {"max_increase": 0.005}  # Moderate RNA increase
    }
    
    # Test different algorithms
    algorithms = [DetectionAlgorithm.CONSERVATIVE, DetectionAlgorithm.BALANCED, DetectionAlgorithm.SENSITIVE]
    
    for algorithm in algorithms:
        detector = DetectorFactory.create_enhancer_detector(algorithm)
        result = detector.detect(strong_enhancer_summary)
        
        print(f"\n{algorithm.value.title()} Algorithm:")
        print(f"   Detected: {result.is_detected}")
        print(f"   Confidence: {result.confidence.value}")
        print(f"   Positive marks: {len(result.positive_marks)}")
        print(f"   Evidence score: {result.total_evidence_score:.2f}")
        print(f"   Interpretation: {result.interpretation}")
    
    return True


def test_tissue_specific_thresholds():
    """Test tissue-specific threshold adjustments."""
    print("\n🧪 Testing Tissue-Specific Thresholds") 
    print("=" * 45)
    
    # Moderate enhancer signal
    moderate_summary = {
        "dnase": {"max_increase": 0.03},
        "chip_histone": {
            "marks": {
                "H3K27ac": {"max_increase": 0.12},
                "H3K4me1": {"max_increase": 0.06}
            }
        },
        "rna_seq": {"max_increase": 0.001}
    }
    
    detector = DetectorFactory.create_enhancer_detector(DetectionAlgorithm.BALANCED)
    
    # Test different tissues
    tissues = [
        ("UBERON:0001264", "pancreatic"),  # Higher threshold
        ("UBERON:0002048", "lung"),        # Lower threshold  
        ("UBERON:0000310", "breast"),      # Standard threshold
    ]
    
    for tissue_id, tissue_name in tissues:
        result = detector.detect(moderate_summary, tissue_id)
        print(f"\n{tissue_name.title()} tissue ({tissue_id}):")
        print(f"   Detected: {result.is_detected}")
        print(f"   Confidence: {result.confidence.value}")
        print(f"   Criteria: {result.criteria_used}")
    
    return True


def test_promoter_detector():
    """Test promoter detection."""
    print("\n🧪 Testing Promoter Detection")
    print("=" * 35)
    
    # Strong promoter signal
    promoter_summary = {
        "dnase": {"max_increase": 0.08},
        "chip_histone": {
            "marks": {
                "H3K4me3": {"max_increase": 0.25},  # Strong promoter mark
                "H3K27ac": {"max_increase": 0.05}   # Some enhancer activity
            }
        },
        "rna_seq": {"max_increase": 0.003}  # Strong transcription
    }
    
    detector = DetectorFactory.create_promoter_detector(DetectionAlgorithm.BALANCED)
    result = detector.detect(promoter_summary)
    
    print(f"   Detected: {result.is_detected}")
    print(f"   Confidence: {result.confidence.value}")
    print(f"   Positive marks: {result.positive_marks}")
    print(f"   Evidence score: {result.total_evidence_score:.2f}")
    print(f"   Interpretation: {result.interpretation}")
    
    return True


def test_edge_cases():
    """Test edge cases and weak signals."""
    print("\n🧪 Testing Edge Cases")
    print("=" * 25)
    
    # Very weak signal - should not be detected
    weak_summary = {
        "dnase": {"max_increase": 0.005},
        "chip_histone": {
            "marks": {
                "H3K27ac": {"max_increase": 0.02},
                "H3K4me1": {"max_increase": 0.01}
            }
        },
        "rna_seq": {"max_increase": 0.0001}
    }
    
    # Empty summary - should not be detected
    empty_summary = {}
    
    detector = DetectorFactory.create_enhancer_detector(DetectionAlgorithm.BALANCED)
    
    # Test weak signal
    weak_result = detector.detect(weak_summary)
    print(f"Weak signal - Detected: {weak_result.is_detected}")
    
    # Test empty data
    empty_result = detector.detect(empty_summary)
    print(f"Empty data - Detected: {empty_result.is_detected}")
    
    # Test sensitive algorithm on weak signal
    sensitive_detector = DetectorFactory.create_enhancer_detector(DetectionAlgorithm.SENSITIVE)
    sensitive_result = sensitive_detector.detect(weak_summary)
    print(f"Sensitive algorithm on weak signal - Detected: {sensitive_result.is_detected}")
    
    return True


def test_confidence_scoring():
    """Test confidence scoring system."""
    print("\n🧪 Testing Confidence Scoring")
    print("=" * 35)
    
    # Test different evidence levels
    test_cases = [
        {
            "name": "Single mark (low confidence)",
            "summary": {
                "dnase": {"max_increase": 0.03},
                "chip_histone": {"marks": {}},
                "rna_seq": {"max_increase": 0.0}
            }
        },
        {
            "name": "Two marks (medium confidence)", 
            "summary": {
                "dnase": {"max_increase": 0.05},
                "chip_histone": {
                    "marks": {"H3K27ac": {"max_increase": 0.15}}
                },
                "rna_seq": {"max_increase": 0.0}
            }
        },
        {
            "name": "Three+ marks (high confidence)",
            "summary": {
                "dnase": {"max_increase": 0.08},
                "chip_histone": {
                    "marks": {
                        "H3K27ac": {"max_increase": 0.20},
                        "H3K4me1": {"max_increase": 0.10}
                    }
                },
                "rna_seq": {"max_increase": 0.003}
            }
        }
    ]
    
    detector = DetectorFactory.create_enhancer_detector(DetectionAlgorithm.BALANCED)
    
    for case in test_cases:
        result = detector.detect(case["summary"])
        print(f"\n{case['name']}:")
        print(f"   Detected: {result.is_detected}")
        print(f"   Confidence: {result.confidence.value}")
        print(f"   Positive marks: {len(result.positive_marks)}")
    
    return True


def test_factory_methods():
    """Test detector factory methods."""
    print("\n🧪 Testing Factory Methods")
    print("=" * 30)
    
    # Test factory creation
    enhancer_detector = DetectorFactory.create_enhancer_detector()
    promoter_detector = DetectorFactory.create_promoter_detector()
    
    print(f"✅ Enhancer detector created: {type(enhancer_detector).__name__}")
    print(f"✅ Promoter detector created: {type(promoter_detector).__name__}")
    
    # Test available algorithms
    algorithms = DetectorFactory.get_available_algorithms()
    print(f"✅ Available algorithms: {[alg.value for alg in algorithms]}")
    
    # Test algorithm descriptions
    for algorithm in algorithms:
        description = DetectorFactory.get_algorithm_description(algorithm)
        print(f"   {algorithm.value}: {description}")
    
    return True


if __name__ == "__main__":
    print("🔬 Professional Detection Modules Test Suite")
    print("=" * 60)
    
    # Run all tests
    test_results = []
    
    test_results.append(("Algorithm Comparison", test_enhancer_detector_algorithms()))
    test_results.append(("Tissue-Specific Thresholds", test_tissue_specific_thresholds()))
    test_results.append(("Promoter Detection", test_promoter_detector()))
    test_results.append(("Edge Cases", test_edge_cases()))
    test_results.append(("Confidence Scoring", test_confidence_scoring()))
    test_results.append(("Factory Methods", test_factory_methods()))
    
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
        print("🎉 All detection module tests passed!")
        sys.exit(0)
    else:
        print("💥 Some tests failed.")
        sys.exit(1)