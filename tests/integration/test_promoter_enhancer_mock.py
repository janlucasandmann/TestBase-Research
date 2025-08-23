"""Integration tests for promoter/enhancer pipeline using mock data."""

import os
import pytest
from pathlib import Path

from ...core.schemas import (
    Assembly, Context, GenomicInterval, PipelineRequest, Variant
)
from ...pipelines.promoter_enhancer import PromoterEnhancerPipeline


@pytest.fixture
def mock_environment():
    """Set up mock environment for testing."""
    original_use_mock = os.environ.get("USE_MOCK")
    os.environ["USE_MOCK"] = "1"
    yield
    if original_use_mock is not None:
        os.environ["USE_MOCK"] = original_use_mock
    else:
        os.environ.pop("USE_MOCK", None)


@pytest.fixture
def pipeline():
    """Create a promoter/enhancer pipeline instance."""
    return PromoterEnhancerPipeline()


@pytest.fixture
def sample_variant():
    """Create a sample variant for testing."""
    return Variant(
        chrom="chr1",
        pos=110000,
        ref="A",
        alt="G",
        assembly=Assembly.HG38
    )


@pytest.fixture
def sample_interval():
    """Create a sample interval for testing."""
    return GenomicInterval(
        chrom="chr1",
        start=100000,
        end=120000,
        assembly=Assembly.HG38
    )


@pytest.fixture
def sample_context():
    """Create a sample biological context."""
    return Context(tissue="hematopoietic")


class TestPromoterEnhancerPipelineMock:
    """Test promoter/enhancer pipeline with mock data."""
    
    def test_variant_analysis_mock(self, mock_environment, pipeline, sample_variant, sample_context):
        """Test variant analysis using mock data."""
        request = PipelineRequest(
            variant=sample_variant,
            context=sample_context
        )
        
        result = pipeline.run(request)
        
        # Verify basic structure
        assert result.mechanism_summary is not None
        assert isinstance(result.mechanism_summary, str)
        assert len(result.mechanism_summary) > 0
        
        # Verify evidence
        assert isinstance(result.evidence, list)
        assert len(result.evidence) > 0
        
        # Check that we have evidence from multiple modalities
        modalities = {e.modality for e in result.evidence}
        assert len(modalities) >= 2  # Should have at least 2 different modalities
        
        # Verify scores
        assert isinstance(result.scores, dict)
        assert len(result.scores) > 0
        
        # Verify figures were generated
        assert isinstance(result.figures, list)
        # Note: Figures might be empty in test environment without display
        
        # Verify metadata
        assert isinstance(result.metadata, dict)
        assert "analysis_type" in result.metadata
        assert result.metadata["analysis_type"] == "variant"
    
    def test_interval_analysis_mock(self, mock_environment, pipeline, sample_interval, sample_context):
        """Test interval analysis using mock data."""
        request = PipelineRequest(
            interval=sample_interval,
            context=sample_context
        )
        
        result = pipeline.run(request)
        
        # Verify basic structure
        assert result.mechanism_summary is not None
        assert isinstance(result.mechanism_summary, str)
        assert len(result.mechanism_summary) > 0
        
        # Verify evidence
        assert isinstance(result.evidence, list)
        assert len(result.evidence) > 0
        
        # Verify scores
        assert isinstance(result.scores, dict)
        assert len(result.scores) > 0
        
        # Verify metadata
        assert isinstance(result.metadata, dict)
        assert "analysis_type" in result.metadata
        assert result.metadata["analysis_type"] == "interval"
    
    def test_empty_context(self, mock_environment, pipeline, sample_variant):
        """Test analysis with empty context."""
        empty_context = Context()
        request = PipelineRequest(
            variant=sample_variant,
            context=empty_context
        )
        
        result = pipeline.run(request)
        
        # Should still work with empty context
        assert result.mechanism_summary is not None
        assert isinstance(result.evidence, list)
        assert isinstance(result.scores, dict)
    
    def test_evidence_structure(self, mock_environment, pipeline, sample_variant, sample_context):
        """Test that evidence items have correct structure."""
        request = PipelineRequest(
            variant=sample_variant,
            context=sample_context
        )
        
        result = pipeline.run(request)
        
        for evidence in result.evidence:
            assert hasattr(evidence, 'modality')
            assert hasattr(evidence, 'description')
            assert hasattr(evidence, 'delta')
            assert hasattr(evidence, 'direction')
            assert hasattr(evidence, 'support_tracks')
            
            # Check that delta is a number
            assert isinstance(evidence.delta, (int, float))
            
            # Check that description is non-empty
            assert len(evidence.description) > 0
            
            # Check that direction is valid
            assert evidence.direction.value in ['up', 'down', 'mixed', 'n/a']
    
    def test_score_aggregation(self, mock_environment, pipeline, sample_variant, sample_context):
        """Test that scores are properly aggregated."""
        request = PipelineRequest(
            variant=sample_variant,
            context=sample_context
        )
        
        result = pipeline.run(request)
        
        # Check for expected score types
        score_keys = result.scores.keys()
        
        # Should have basic aggregation scores
        basic_scores = ['mean_delta', 'max_delta', 'min_delta', 'max_abs_delta']
        found_basic = any(score in score_keys for score in basic_scores)
        assert found_basic, f"Should have basic scores, got: {list(score_keys)}"
        
        # All scores should be numeric
        for key, value in result.scores.items():
            assert isinstance(value, (int, float)), f"Score {key} should be numeric, got {type(value)}"
    
    def test_mechanism_summary_content(self, mock_environment, pipeline, sample_variant, sample_context):
        """Test that mechanism summary contains meaningful content."""
        request = PipelineRequest(
            variant=sample_variant,
            context=sample_context
        )
        
        result = pipeline.run(request)
        
        summary = result.mechanism_summary.lower()
        
        # Should mention regulatory concepts
        regulatory_terms = [
            'increases', 'decreases', 'enhancer', 'promoter', 'activity',
            'chromatin', 'binding', 'accessibility', 'regulatory', 'modality'
        ]
        
        found_terms = [term for term in regulatory_terms if term in summary]
        assert len(found_terms) > 0, f"Summary should contain regulatory terms. Summary: {result.mechanism_summary}"
        
        # Should be a reasonable length (not too short or too long)
        assert 10 < len(result.mechanism_summary) < 500
    
    def test_primary_direction_calculation(self, mock_environment, pipeline, sample_variant, sample_context):
        """Test that primary direction is calculated correctly."""
        request = PipelineRequest(
            variant=sample_variant,
            context=sample_context
        )
        
        result = pipeline.run(request)
        
        if result.evidence:
            primary_direction = result.get_primary_direction()
            assert primary_direction.value in ['up', 'down', 'mixed', 'n/a']
    
    def test_top_evidence_selection(self, mock_environment, pipeline, sample_variant, sample_context):
        """Test that top evidence is selected correctly."""
        request = PipelineRequest(
            variant=sample_variant,
            context=sample_context
        )
        
        result = pipeline.run(request)
        
        if len(result.evidence) > 1:
            top_evidence = result.get_top_evidence(n=3)
            
            # Should return at most 3 items
            assert len(top_evidence) <= 3
            
            # Should be sorted by absolute delta (descending)
            for i in range(len(top_evidence) - 1):
                assert abs(top_evidence[i].delta) >= abs(top_evidence[i + 1].delta)
    
    @pytest.mark.parametrize("assembly", [Assembly.HG19, Assembly.HG38])
    def test_different_assemblies(self, mock_environment, pipeline, sample_context, assembly):
        """Test analysis with different genome assemblies."""
        variant = Variant(
            chrom="chr1",
            pos=110000,
            ref="A",
            alt="G",
            assembly=assembly
        )
        
        request = PipelineRequest(
            variant=variant,
            context=sample_context
        )
        
        result = pipeline.run(request)
        
        # Should work with any assembly
        assert result.mechanism_summary is not None
        assert isinstance(result.evidence, list)
    
    def test_large_interval(self, mock_environment, pipeline, sample_context):
        """Test analysis with a larger interval."""
        large_interval = GenomicInterval(
            chrom="chr1",
            start=100000,
            end=150000,  # 50kb interval
            assembly=Assembly.HG38
        )
        
        request = PipelineRequest(
            interval=large_interval,
            context=sample_context
        )
        
        result = pipeline.run(request)
        
        # Should handle larger intervals
        assert result.mechanism_summary is not None
        assert isinstance(result.evidence, list)
    
    def test_invalid_request(self, mock_environment, pipeline, sample_context):
        """Test that invalid requests are handled appropriately."""
        # Request with neither variant nor interval
        with pytest.raises(ValueError):
            request = PipelineRequest(context=sample_context)
    
    def test_report_generation(self, mock_environment, pipeline, sample_variant, sample_context):
        """Test that HTML report is generated."""
        request = PipelineRequest(
            variant=sample_variant,
            context=sample_context
        )
        
        result = pipeline.run(request)
        
        # Check that report path is in metadata
        assert "report_path" in result.metadata
        
        # Check that the report file exists
        report_path = result.metadata["report_path"]
        if report_path:
            assert Path(report_path).exists()
            
            # Check that it's an HTML file
            assert str(report_path).endswith('.html')
            
            # Check that it has some content
            content = Path(report_path).read_text()
            assert len(content) > 0
            assert '<html>' in content or '<!DOCTYPE html>' in content.lower()


class TestMockDataConsistency:
    """Test that mock data is consistent and realistic."""
    
    def test_mock_fixture_exists(self):
        """Test that the mock fixture file exists."""
        from ...core.config import config
        fixture_path = config.FIXTURES_DIR / "alphagenome_promoter_enhancer_sample.json"
        assert fixture_path.exists(), f"Mock fixture should exist at {fixture_path}"
    
    def test_mock_data_structure(self, mock_environment, pipeline, sample_variant, sample_context):
        """Test that mock data has the expected structure."""
        from ...clients.alphagenome import AlphaGenomeClient
        
        client = AlphaGenomeClient()
        response = client._load_mock_response()
        
        # Check basic structure
        assert "coordinates" in response
        assert "predictions" in response
        
        # Check coordinates
        coordinates = response["coordinates"]
        assert isinstance(coordinates, list)
        assert len(coordinates) > 0
        assert all(isinstance(c, (int, float)) for c in coordinates)
        
        # Check predictions
        predictions = response["predictions"]
        assert isinstance(predictions, dict)
        assert len(predictions) > 0
        
        # Check individual tracks
        for track_id, track_data in predictions.items():
            assert "ref" in track_data
            assert "alt" in track_data
            assert "metadata" in track_data
            
            ref_values = track_data["ref"]
            alt_values = track_data["alt"]
            
            assert isinstance(ref_values, list)
            assert isinstance(alt_values, list)
            assert len(ref_values) == len(alt_values)
            assert len(ref_values) > 0
            
            # Values should be numeric
            assert all(isinstance(v, (int, float)) for v in ref_values)
            assert all(isinstance(v, (int, float)) for v in alt_values)
    
    def test_mock_modalities_coverage(self, mock_environment, pipeline, sample_variant, sample_context):
        """Test that mock data covers the required modalities."""
        from ...clients.alphagenome import AlphaGenomeClient
        
        client = AlphaGenomeClient()
        response = client._load_mock_response()
        
        predictions = response["predictions"]
        
        # Check that we have tracks for different modalities
        modalities_found = set()
        for track_data in predictions.values():
            metadata = track_data.get("metadata", {})
            modality = metadata.get("modality")
            if modality:
                modalities_found.add(modality)
        
        required_modalities = {"TSS_CAGE", "HISTONE", "ATAC_DNASE", "TF_BIND"}
        assert modalities_found.issuperset(required_modalities), \
            f"Mock data should cover required modalities. Found: {modalities_found}, Required: {required_modalities}"