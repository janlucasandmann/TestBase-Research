# AlphaGenome Cancer Research Agent

A professional, modular AI agent for cancer biology research using real mutation data from cBioPortal and regulatory predictions from Google's AlphaGenome API.

## 🎯 Overview

This agent answers cancer biology research questions by:

1. **Fetching real mutation data** from cBioPortal for specific genes and cancer types
2. **Analyzing regulatory effects** using AlphaGenome's deep learning predictions
3. **Interpreting results** with evidence-based criteria
4. **Generating comprehensive reports** with visualizations

## 🏗️ Architecture

### Modular Design

```
src/
├── clients/           # API clients (AlphaGenome, cBioPortal)
├── pipelines/         # Analysis pipelines (enhancer detection, etc.)
├── core/             # Shared schemas and utilities
├── reports/          # Report generation
├── viz/              # Visualization generation
└── tests/            # Comprehensive test suites
```

### Key Principles

- **No mock data** - All analyses use real API data
- **Professional error handling** - Graceful failures with detailed logging
- **Modular architecture** - Easy to extend with new pipeline types
- **Scientific rigor** - Evidence-based criteria and transparent reporting

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd alphagenome_agent

# Install dependencies
pip install -r requirements.txt

# Set up environment
export ALPHAGENOME_API_KEY="your-api-key-here"
```

### Basic Usage

```python
from src.pipelines.enhancer import EnhancerDetectionPipeline

# Initialize pipeline
pipeline = EnhancerDetectionPipeline(
    alphagenome_api_key="your-api-key",
    output_dir="data/outputs"
)

# Run analysis
result = pipeline.run(
    gene="KRAS",
    cancer_type="pancreatic", 
    max_mutations=10
)

print(f"Answer: {result['research_question']}")
print(f"Enhancers detected: {result['enhancers_detected']}/{result['mutations_analyzed']}")
```

### Command Line Interface

```bash
# Run enhancer detection pipeline
python -m src.pipelines.enhancer --gene KRAS --cancer pancreatic --max-mutations 10

# With custom output directory
python -m src.pipelines.enhancer --gene TP53 --cancer breast --output-dir my_results
```

## 📊 Available Pipelines

### 1. Enhancer Detection Pipeline

**Research Question**: "Do [GENE] mutations create enhancer-like regulatory elements in [CANCER] cancer?"

**Scientific Criteria**:
- DNase accessibility increase (open chromatin)
- H3K27ac increase (active enhancer mark)
- H3K4me1 increase (enhancer mark)  
- RNA expression increase
- Minimum evidence threshold (configurable)

**Example Results**:
```
✅ ANSWER: YES - 7/10 mutations (70%) show enhancer-like signatures
   High confidence: 3 mutations
   Medium confidence: 4 mutations
   Evidence: DNase ↑, H3K27ac ↑, RNA ↑
```

## 🧪 Testing

### Run All Tests

```bash
# Test clients
python run_tests.py

# Test pipelines  
python src/pipelines/tests/test_enhancer_pipeline.py

# Test specific components
pytest src/clients/tests/ -v
```

### Integration Tests

Tests verify:
- Real cBioPortal mutation fetching
- Real AlphaGenome API calls
- End-to-end pipeline execution
- Error handling and edge cases
- Report and visualization generation

## 📈 Extending the System

### Adding New Pipelines

1. **Inherit from BasePipeline**:
```python
from src.pipelines.base import BasePipeline

class MyCustomPipeline(BasePipeline):
    def analyze_variant(self, mutation, tissue_ontology_id):
        # Your analysis logic
        return {"status": "success", ...}
    
    def create_visualizations(self, analysis_result):
        # Your visualization logic
        return ["path/to/plot.png"]
    
    def generate_report(self, mutation_data, analysis_results, research_question):
        # Your reporting logic
        return "path/to/report.html"
```

2. **Implement Required Methods**:
   - `analyze_variant()` - Core analysis logic
   - `create_visualizations()` - Generate plots
   - `generate_report()` - Create comprehensive reports

3. **Add Tests**:
```python
def test_my_custom_pipeline():
    pipeline = MyCustomPipeline(alphagenome_api_key=api_key)
    result = pipeline.run(gene="KRAS", cancer_type="pancreatic")
    assert result["status"] == "success"
```

### Adding New Cancer Types

Update the tissue ontology mapping in `src/pipelines/base.py`:

```python
DEFAULT_TISSUE_ONTOLOGY = {
    "new_cancer_type": "UBERON:0001234",  # Add your mapping
    # ... existing mappings
}
```

## 🔬 Scientific Accuracy

### Data Sources
- **cBioPortal**: Real mutation data from TCGA and other studies
- **AlphaGenome**: Google's state-of-the-art regulatory predictions
- **UBERON**: Standardized tissue ontology

### Validation
- All predictions are computational and require wet-lab validation
- Results include confidence levels and evidence criteria
- Transparent reporting of methods and limitations

### Reproducibility
- Deterministic analysis with versioned criteria
- Complete audit trail in reports
- Source data and parameters preserved

## 🛠️ Configuration

### Enhancer Detection Criteria

Customize detection thresholds:

```python
custom_criteria = {
    "dnase_min_increase": 0.01,     # DNase accessibility
    "h3k27ac_min_increase": 0.1,    # Active enhancer mark
    "h3k4me1_min_increase": 0.05,   # Enhancer mark  
    "rna_min_increase": 0.001,      # RNA expression
    "min_marks_required": 2         # Evidence threshold
}

pipeline = EnhancerDetectionPipeline(
    alphagenome_api_key=api_key,
    enhancer_criteria=custom_criteria
)
```

### Output Directories

```python
pipeline = EnhancerDetectionPipeline(
    alphagenome_api_key=api_key,
    output_dir="custom/output/path"  # Reports and visualizations
)
```

## 📋 Requirements

### API Keys
- **AlphaGenome API Key**: Required for regulatory predictions
- **cBioPortal**: Public API (no key required)

### Dependencies
- `alphagenome` - Official AlphaGenome Python client
- `requests` - HTTP requests for cBioPortal
- `matplotlib`, `seaborn` - Visualizations
- `pydantic` - Data validation
- `jinja2` - Report templating

### Python Version
- Python 3.8+

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-pipeline`
3. **Add comprehensive tests**
4. **Follow coding standards**: Black formatting, type hints
5. **Submit pull request**

### Development Guidelines

- **No mock data** - Always use real APIs
- **Comprehensive testing** - Test all error cases
- **Scientific rigor** - Evidence-based criteria
- **Clear documentation** - Explain methods and limitations

## 📄 Legacy Components

This repository also contains legacy components from earlier development:

### Legacy CLI Interface
```bash
# Legacy promoter-enhancer analysis (uses AlphaGenome directly)
python -m src.cli.main run promoter-enhancer \
  --interval "chr1:100000-120000" \
  --assembly hg38 \
  --tissue "hematopoietic" \
  --outdir data/outputs
```

### Legacy Features
- Direct AlphaGenome interval analysis
- TSS/CAGE, histone marks, chromatin accessibility analysis
- Mock data support for development
- HTML report generation with embedded figures

## 🙋 Support

- **Issues**: [GitHub Issues](link-to-issues)
- **Documentation**: [Full Documentation](link-to-docs)
- **Examples**: See `examples/` directory

---

**Built with scientific integrity and professional standards for cancer research.**