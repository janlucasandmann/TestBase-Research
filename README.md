# TestBase Research

A powerful AI-driven pipeline for discovering novel regulatory mechanisms in cancer using AlphaGenome's deep learning predictions. This pipeline focuses on the 98% non-coding genome to reveal cancer mechanisms invisible to traditional approaches.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![AlphaGenome](https://img.shields.io/badge/AlphaGenome-Powered-green.svg)](https://github.com/google-deepmind/alphagenome)

## 🚀 Quick Start for AI Agents

```python
from alphagenome_cancer_pipeline import analyze_regulatory_cancer_mechanism

# Simply ask a question and get comprehensive analysis
results = analyze_regulatory_cancer_mechanism(
    question="Which regulatory variants create enhancers that activate MYC in lung cancer?",
    gene="MYC",
    tissue="lung",
    api_key="YOUR_ALPHAGENOME_API_KEY"
)

print(results['report'])  # Markdown report with visualizations
```

## 📋 Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [API Key Setup](#api-key-setup)
- [Usage Examples](#usage-examples)
- [Pipeline Capabilities](#pipeline-capabilities)
- [Output Files](#output-files)
- [AI Agent Integration](#ai-agent-integration)
- [Troubleshooting](#troubleshooting)

## 🔬 Overview

This pipeline leverages AlphaGenome to:
- Discover how non-coding variants create cancer-driving enhancers
- Understand tissue-specific vulnerabilities in cancer
- Map long-range regulatory interactions (up to 1Mb)
- Predict splicing dysregulation from variants
- Generate publication-quality visualizations and reports

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/TestBase-Research.git
   cd TestBase-Research
   ```

2. **Install dependencies:**
   ```bash
   pip install alphagenome pandas numpy matplotlib
   ```

3. **Verify installation:**
   ```python
   import alphagenome
   print("AlphaGenome installed successfully!")
   ```

## 🔑 API Key Setup

You need an AlphaGenome API key. Set it up using one of these methods:

**Option 1: Environment Variable (Recommended)**
```bash
export ALPHAGENOME_API_KEY="your_api_key_here"
```

**Option 2: Direct in Code**
```python
api_key = "your_api_key_here"
```

**Option 3: Config File**
Create `.env` file:
```
ALPHAGENOME_API_KEY=your_api_key_here
```

## 💡 Usage Examples

### 1. Simple Question-Based Analysis

```python
from alphagenome_cancer_pipeline import analyze_regulatory_cancer_mechanism

# Ask about enhancer creation
results = analyze_regulatory_cancer_mechanism(
    question="What enhancers control TAL1 expression in blood cancer?",
    gene="TAL1",
    tissue="blood",
    api_key="YOUR_KEY"
)
```

### 2. Analyze Specific Variants

```python
from alphagenome_cancer_pipeline import AlphaGenomeCancerPipeline, RegulatoryVariant

# Initialize pipeline
pipeline = AlphaGenomeCancerPipeline(api_key="YOUR_KEY")

# Define a variant (e.g., TAL1 enhancer insertion)
variant = RegulatoryVariant(
    chromosome="chr1",
    position=47239296,
    ref="C",
    alt="CCGTTTCCTAACC",
    variant_id="TAL1_insertion",
    cancer_type="T-ALL"
)

# Discover if it creates an enhancer
enhancer_results = pipeline.discover_de_novo_enhancers(
    cancer_variants=[variant],
    tissue="blood",
    nearby_genes=["TAL1", "STIL"]
)

# Check tissue specificity
tissue_results = pipeline.compare_tissue_specificity(
    variant=variant,
    tissues=["blood", "brain", "lung", "liver"]
)
```

### 3. Complete Analysis with Visualization and Report

```python
from alphagenome_cancer_pipeline import AlphaGenomeCancerPipeline, RegulatoryVariant
from alphagenome.models import dna_client

# Initialize
pipeline = AlphaGenomeCancerPipeline(api_key="YOUR_KEY")

# Define variant
variant = RegulatoryVariant(
    chromosome="chr8",
    position=128750000,
    ref="G",
    alt="A",
    variant_id="MYC_enhancer_variant"
)

# Get AlphaGenome predictions
ag_variant = variant.to_alphagenome_variant()
interval = ag_variant.reference_interval.resize(131_072)

output = pipeline.model.predict_variant(
    interval=interval,
    variant=ag_variant,
    requested_outputs=[
        dna_client.OutputType.RNA_SEQ,
        dna_client.OutputType.DNASE,
        dna_client.OutputType.CHIP_HISTONE,
    ],
    ontology_terms=[pipeline.tissue_ontology['lung']]
)

# Create visualization
viz_path = pipeline.visualize_variant_impact(
    variant=variant,
    output=output,
    interval=interval,
    tissue_name="lung"
)

# Generate report
report_path = pipeline.generate_markdown_report(
    analysis_type="De Novo Enhancers",
    results=enhancer_results,
    visualizations=[viz_path]
)

print(f"Report saved: {report_path}")
print(f"Visualization saved: {viz_path}")
```

### 4. Batch Analysis of Multiple Variants

```python
# Analyze a cohort of variants
variants = [
    {"chromosome": "chr1", "position": 47239296, "ref": "C", "alt": "CCGTTTCCTAACC", "variant_id": "var1"},
    {"chromosome": "chr8", "position": 128750000, "ref": "G", "alt": "A", "variant_id": "var2"},
    {"chromosome": "chr12", "position": 25398284, "ref": "C", "alt": "T", "variant_id": "var3"}
]

# Convert to RegulatoryVariant objects
reg_variants = [RegulatoryVariant(**v) for v in variants]

# Run analysis
results = pipeline.find_convergent_mechanisms(
    patient_variants={"cohort": reg_variants},
    target_genes=["TAL1", "MYC", "KRAS"],
    tissue="lung"
)
```

## 🧬 Pipeline Capabilities

### 1. **Regulatory Landscape Mapping**
```python
landscape = pipeline.analyze_regulatory_landscape(
    gene="MYC",
    tissue="lung",
    window_size=1_048_576  # 1Mb window
)
```
- Maps all enhancers, silencers, and regulatory elements
- Identifies tissue-specific elements
- Discovers long-range interactions

### 2. **De Novo Enhancer Discovery**
```python
enhancers = pipeline.discover_de_novo_enhancers(
    cancer_variants=[variant],
    tissue="blood",
    nearby_genes=["TAL1"]
)
```
- Finds variants that create new enhancers
- Predicts affected genes
- Warns about oncogene activation

### 3. **Tissue Specificity Analysis**
```python
tissue_effects = pipeline.compare_tissue_specificity(
    variant=variant,
    tissues=["blood", "brain", "lung", "liver"]
)
```
- Explains why variants cause cancer in specific tissues
- Compares regulatory impact across cell types
- Identifies tissue-specific vulnerabilities

### 4. **Long-Range Interaction Analysis**
```python
interactions = pipeline.analyze_long_range_interactions(
    gene="MYC",
    cancer_variants=variants,
    tissue="colon",
    max_distance=1_048_576
)
```
- Maps 3D chromatin interactions
- Discovers enhancer hijacking
- Identifies TAD disruptions

### 5. **Splicing Dysregulation Prediction**
```python
splicing = pipeline.predict_splicing_dysregulation(
    gene="TP53",
    variants=variants,
    tissue="breast"
)
```
- Predicts exon skipping
- Identifies isoform switches
- Maps functional impacts

## 📊 Output Files

### Visualizations (`visualizations/`)
- Multi-track plots showing REF vs ALT allele effects
- Format: `{variant_id}_{chr}_{position}.png`
- High-resolution (300 DPI) for publication

### Reports (`reports/`)
- Comprehensive markdown reports
- Format: `{analysis_type}_report_{timestamp}.md`
- Includes embedded visualizations and interpretations

### Data Files
- JSON results: `{analysis_name}_results.json`
- Processed variant data in pandas-compatible format

## 🤖 AI Agent Integration

### For LLM/AI Agents

The pipeline is designed for easy AI agent integration:

```python
# Simple interface for AI agents
from alphagenome_cancer_pipeline import analyze_regulatory_cancer_mechanism

# The AI agent can form questions naturally
questions = [
    "Which variants create enhancers for MYC in lung cancer?",
    "Why does TERT promoter mutation cause cancer in brain but not blood?",
    "What regulatory elements control EGFR in lung tissue?",
    "How do distant variants affect TP53 expression?"
]

# Process each question
for question in questions:
    # Extract gene and tissue from question (AI can do this)
    gene = extract_gene(question)  # AI extracts: "MYC", "TERT", etc.
    tissue = extract_tissue(question)  # AI extracts: "lung", "brain", etc.
    
    # Run analysis
    results = analyze_regulatory_cancer_mechanism(
        question=question,
        gene=gene,
        tissue=tissue,
        api_key=api_key
    )
    
    # Results include:
    # - results['report']: Full markdown report
    # - results['visualizations']: List of generated plots
    # - results['analysis_results']: Structured data
```

### Automated Workflow

```python
# Complete automated workflow for AI agents
def ai_agent_cancer_analysis(research_question, variants=None):
    """
    Automated pipeline for AI agents to answer cancer research questions
    
    Args:
        research_question: Natural language question
        variants: Optional list of variants to analyze
    
    Returns:
        Dictionary with report, visualizations, and recommendations
    """
    
    # 1. Parse question (AI agent capability)
    parsed = parse_research_question(research_question)
    gene = parsed['gene']
    tissue = parsed['tissue']
    analysis_type = parsed['analysis_type']
    
    # 2. Initialize pipeline
    pipeline = AlphaGenomeCancerPipeline(api_key=get_api_key())
    
    # 3. Run appropriate analysis
    if analysis_type == "enhancer":
        results = pipeline.discover_de_novo_enhancers(
            cancer_variants=variants or [],
            tissue=tissue,
            nearby_genes=[gene]
        )
    elif analysis_type == "landscape":
        results = pipeline.analyze_regulatory_landscape(gene, tissue)
    elif analysis_type == "tissue_specific":
        results = pipeline.compare_tissue_specificity(
            variant=variants[0] if variants else None,
            tissues=["blood", "brain", "lung", "liver"]
        )
    
    # 4. Generate visualizations
    visualizations = []
    if variants:
        for variant in variants[:5]:  # Limit to 5 for performance
            viz_path = create_variant_visualization(pipeline, variant, tissue)
            visualizations.append(viz_path)
    
    # 5. Generate comprehensive report
    report_path = pipeline.generate_markdown_report(
        analysis_type=analysis_type.title(),
        results=results,
        visualizations=visualizations
    )
    
    # 6. Extract key findings for AI summary
    key_findings = extract_key_findings(results)
    
    return {
        "status": "success",
        "question": research_question,
        "report_path": report_path,
        "visualizations": visualizations,
        "key_findings": key_findings,
        "therapeutic_recommendations": generate_recommendations(results),
        "next_steps": suggest_follow_up_analyses(results)
    }
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Error: No module named 'alphagenome'**
   ```bash
   pip install alphagenome
   ```

2. **API Key Error**
   ```python
   # Check if key is set
   import os
   print(os.environ.get('ALPHAGENOME_API_KEY', 'Not set'))
   ```

3. **Sequence Length Error**
   ```python
   # Use supported lengths
   SUPPORTED_LENGTHS = [2048, 16384, 131072, 524288, 1048576]
   interval = interval.resize(131072)  # Use 131kb
   ```

4. **Memory Issues with Large Analyses**
   ```python
   # Process in batches
   for i in range(0, len(variants), 10):
       batch = variants[i:i+10]
       results = analyze_batch(batch)
   ```

### Debug Mode

```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test with a known variant
test_variant = RegulatoryVariant(
    chromosome="chr1",
    position=47239296,
    ref="C",
    alt="CCGTTTCCTAACC",
    variant_id="test"
)
```

## 📚 Additional Resources

- **Documentation**: See `alphagenome_cancer_capabilities.md` for detailed explanations
- **Examples**: Run `regulatory_analysis_examples.py` for demonstrations
- **Agent Guide**: Read `agent_guide.md` for AI integration details
- **Project Structure**: See `PROJECT_STRUCTURE.md` for file organization

## 🎯 Key Features for Cancer Research

1. **Non-Coding Focus**: Analyzes the 98% of genome ignored by traditional methods
2. **Multimodal Integration**: Combines expression, chromatin, and 3D structure
3. **Tissue Specificity**: Understands cell-type-specific effects
4. **Long-Range Effects**: Discovers regulatory interactions up to 1Mb away
5. **Clinical Relevance**: Provides therapeutic recommendations

## 📧 Support

For issues or questions:
1. Check the troubleshooting section
2. Review example scripts
3. Consult AlphaGenome documentation

---

*This pipeline enables discovery of cancer mechanisms invisible to traditional genomic approaches.*