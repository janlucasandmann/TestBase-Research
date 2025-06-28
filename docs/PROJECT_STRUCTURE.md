# AlphaGenome Cancer Research Pipeline - Project Structure

## Overview
This project provides an AI-powered pipeline for discovering novel regulatory mechanisms in cancer using AlphaGenome.

## Directory Structure

```
TestBase-research/
│
├── Core Pipeline Files
│   ├── alphagenome_cancer_pipeline.py    # Main pipeline with all analysis methods
│   ├── research_pipeline.py              # Original cBioPortal integration pipeline
│   └── create_real_visualizations.py     # Script to generate actual visualizations
│
├── Documentation
│   ├── alphagenome_cancer_capabilities.md # Comprehensive guide on what AlphaGenome can do
│   ├── agent_guide.md                     # Guide for AI agents using the pipeline
│   ├── AlphaGenome_Pipeline_Summary.md    # Quick summary of capabilities
│   └── PROJECT_STRUCTURE.md               # This file
│
├── Examples & Demos
│   ├── regulatory_analysis_examples.py    # 6 example analyses demonstrating capabilities
│   ├── demo_visualization.py              # Creates demonstration visualizations
│   └── demo_visualizations/               # Sample visualization outputs
│       ├── TAL1_variant_impact_demo.png
│       └── MYC_regulatory_landscape_demo.png
│
├── Analysis Outputs
│   ├── visualizations/                    # Real AlphaGenome visualizations
│   │   ├── TAL1_enhancer_insertion_chr1_47239296.png
│   │   └── MYC_regulatory_landscape_lung.png
│   │
│   └── reports/                          # Generated markdown reports
│       ├── de_novo_enhancers_report_*.md
│       ├── regulatory_landscape_report_*.md
│       └── tissue_specificity_report_*.md
│
├── cBioPortal Integration
│   └── cbioportal/                       # cBioPortal data and analysis scripts
│       ├── query_data.py                 # Fetch mutation data
│       ├── prepare_data.py               # Format for AlphaGenome
│       ├── test_alphagenome.py           # Integration tests
│       └── visualize_results.py          # Result visualization
│
├── AlphaGenome Package
│   └── alphagenome/                      # Official AlphaGenome Python package
│       ├── src/alphagenome/              # Source code
│       ├── colabs/                       # Example notebooks
│       └── docs/                         # Package documentation
│
└── Archive
    └── archive/                          # Old test files and results
        ├── old_tests/
        └── old_results/
```

## Key Components

### 1. Main Pipeline (`alphagenome_cancer_pipeline.py`)
The core pipeline provides these analysis methods:
- `analyze_regulatory_landscape()` - Map all regulatory elements
- `discover_de_novo_enhancers()` - Find variants creating new enhancers
- `analyze_long_range_interactions()` - Discover distant regulatory effects
- `compare_tissue_specificity()` - Understand tissue-specific impacts
- `find_convergent_mechanisms()` - Identify shared regulatory patterns
- `predict_splicing_dysregulation()` - Analyze splicing changes
- `visualize_variant_impact()` - Create multi-track visualizations
- `generate_markdown_report()` - Generate comprehensive reports

### 2. Visualization System
- Multi-track plots showing REF vs ALT allele effects
- RNA-seq, DNase accessibility, and histone modification tracks
- Variant position annotations
- High-resolution PNG outputs suitable for publication

### 3. Report Generation
- Professional markdown reports with embedded visualizations
- Clinical interpretations and therapeutic recommendations
- Methods descriptions and key findings tables
- Automatic timestamp and analysis tracking

## Usage Examples

### Basic Analysis
```python
from alphagenome_cancer_pipeline import AlphaGenomeCancerPipeline, RegulatoryVariant

# Initialize
pipeline = AlphaGenomeCancerPipeline(api_key="YOUR_KEY")

# Define variant
variant = RegulatoryVariant(
    chromosome="chr1",
    position=47239296,
    ref="C",
    alt="CCGTTTCCTAACC",
    variant_id="TAL1_insertion"
)

# Run analysis
results = pipeline.discover_de_novo_enhancers(
    cancer_variants=[variant],
    tissue="blood",
    nearby_genes=["TAL1"]
)
```

### Generate Visualizations
```python
# Get AlphaGenome predictions
output = pipeline.model.predict_variant(
    interval=interval,
    variant=ag_variant,
    requested_outputs=[
        dna_client.OutputType.RNA_SEQ,
        dna_client.OutputType.DNASE,
        dna_client.OutputType.CHIP_HISTONE,
    ],
    ontology_terms=[tissue_ontology]
)

# Create visualization
viz_path = pipeline.visualize_variant_impact(
    variant=variant,
    output=output,
    interval=interval,
    tissue_name="blood"
)

# Generate report
report_path = pipeline.generate_markdown_report(
    analysis_type="De Novo Enhancers",
    results=results,
    visualizations=[viz_path]
)
```

## Key Features

1. **Focus on Non-Coding Genome**: Analyzes the 98% of genome ignored by traditional approaches
2. **Multimodal Predictions**: Integrates expression, chromatin, and 3D structure data
3. **Tissue Specificity**: Understands why variants affect specific cell types
4. **Long-Range Effects**: Discovers regulatory interactions up to 1Mb away
5. **Clinical Relevance**: Provides interpretations and therapeutic recommendations

## Requirements

- Python 3.7+
- AlphaGenome package
- API key for AlphaGenome
- Dependencies: pandas, numpy, matplotlib

## Getting Started

1. Install dependencies:
   ```bash
   pip install alphagenome pandas numpy matplotlib
   ```

2. Set your API key:
   ```bash
   export ALPHAGENOME_API_KEY="your_key_here"
   ```

3. Run example analysis:
   ```bash
   python create_real_visualizations.py
   ```

## Output Files

- **Visualizations**: High-resolution PNG files in `visualizations/`
- **Reports**: Markdown reports with embedded images in `reports/`
- **Data**: JSON files with analysis results

## Future Enhancements

1. Batch processing for multiple variants
2. Integration with clinical databases
3. Machine learning for pattern discovery
4. Web interface for interactive exploration
5. Automated experimental validation design

---

*This pipeline enables discovery of cancer mechanisms invisible to traditional genomic approaches by leveraging AlphaGenome's unique ability to predict regulatory effects in the non-coding genome.*