# AI Agent Integration Guide for AlphaGenome Cancer Research Pipeline

## Overview

This guide helps AI agents use the AlphaGenome cancer research pipeline to discover novel regulatory mechanisms in cancer. The pipeline focuses on the 98% non-coding genome where traditional methods fail.

## Quick Start for AI Agents

### Simple One-Line Analysis

```python
from alphagenome_cancer_pipeline import analyze_regulatory_cancer_mechanism

# Just provide a question - the pipeline handles the rest
results = analyze_regulatory_cancer_mechanism(
    question="Which regulatory variants create enhancers for MYC in lung cancer?",
    gene="MYC",
    tissue="lung",
    api_key="YOUR_API_KEY"
)

print(results['report'])
```

## Types of Questions You Can Answer

### 1. 🔍 Enhancer Discovery
**Question Pattern**: "Which variants create enhancers for [GENE] in [TISSUE]?"

**Example**:
```python
results = analyze_regulatory_cancer_mechanism(
    question="What variants create enhancers that activate TAL1 in blood cancer?",
    gene="TAL1",
    tissue="blood",
    api_key=api_key
)
```

**Returns**: 
- New enhancers created by variants
- Affected genes
- Tissue-specific activity
- Warnings about oncogene activation

### 2. 🌍 Regulatory Landscape
**Question Pattern**: "What regulatory elements control [GENE] in [TISSUE]?"

**Example**:
```python
results = analyze_regulatory_cancer_mechanism(
    question="What enhancers and silencers control MYC expression in lung tissue?",
    gene="MYC",
    tissue="lung",
    api_key=api_key
)
```

**Returns**:
- All enhancers within 1Mb
- Active promoters
- Silencer elements
- 3D chromatin interactions

### 3. 🎯 Tissue Specificity
**Question Pattern**: "Why does [VARIANT] cause cancer in [TISSUE1] but not [TISSUE2]?"

**Example**:
```python
results = analyze_regulatory_cancer_mechanism(
    question="Why do TERT promoter mutations cause cancer in brain but not blood?",
    gene="TERT",
    tissue="brain",
    variants=[{
        "chromosome": "chr5",
        "position": 1295228,
        "ref": "G",
        "alt": "A",
        "variant_id": "TERT_C228T"
    }],
    api_key=api_key
)
```

**Returns**:
- Tissue-specific regulatory impacts
- Comparative analysis across tissues
- Cell-type-specific transcription factors

### 4. 🌉 Long-Range Interactions
**Question Pattern**: "How do distant variants affect [GENE] in [TISSUE]?"

**Example**:
```python
results = analyze_regulatory_cancer_mechanism(
    question="Which variants 500kb away can still activate MYC?",
    gene="MYC",
    tissue="colon",
    api_key=api_key
)
```

**Returns**:
- 3D chromatin loops
- Enhancer hijacking events
- TAD boundary disruptions

### 5. ✂️ Splicing Effects
**Question Pattern**: "How do variants affect [GENE] splicing in [TISSUE]?"

**Example**:
```python
results = analyze_regulatory_cancer_mechanism(
    question="Which variants cause TP53 exon skipping in breast cancer?",
    gene="TP53",
    tissue="breast",
    api_key=api_key
)
```

**Returns**:
- Predicted splice site changes
- Exon inclusion/exclusion
- Functional impact on protein

## Complete Workflow for Complex Analyses

```python
from alphagenome_cancer_pipeline import AlphaGenomeCancerPipeline, RegulatoryVariant

# For more complex analyses requiring multiple steps
def comprehensive_cancer_analysis(patient_variants, target_gene, tissue):
    """
    Complete analysis workflow with visualizations and reports
    """
    
    # 1. Initialize pipeline
    pipeline = AlphaGenomeCancerPipeline(api_key="YOUR_KEY")
    
    # 2. Convert variants to proper format
    reg_variants = []
    for v in patient_variants:
        reg_variants.append(RegulatoryVariant(
            chromosome=v['chr'],
            position=v['pos'],
            ref=v['ref'],
            alt=v['alt'],
            variant_id=v.get('id', f"{v['chr']}_{v['pos']}")
        ))
    
    # 3. Run multiple analyses
    results = {}
    
    # Check for de novo enhancers
    results['enhancers'] = pipeline.discover_de_novo_enhancers(
        cancer_variants=reg_variants,
        tissue=tissue,
        nearby_genes=[target_gene]
    )
    
    # Analyze tissue specificity
    if reg_variants:
        results['tissue_spec'] = pipeline.compare_tissue_specificity(
            variant=reg_variants[0],
            tissues=['blood', 'brain', 'lung', 'liver']
        )
    
    # Map regulatory landscape
    results['landscape'] = pipeline.analyze_regulatory_landscape(
        gene=target_gene,
        tissue=tissue
    )
    
    # 4. Generate visualizations
    visualizations = []
    for variant in reg_variants[:3]:  # Top 3 variants
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
            ontology_terms=[pipeline.tissue_ontology[tissue]]
        )
        
        viz_path = pipeline.visualize_variant_impact(
            variant=variant,
            output=output,
            interval=interval,
            tissue_name=tissue
        )
        visualizations.append(viz_path)
    
    # 5. Generate comprehensive report
    report_path = pipeline.generate_markdown_report(
        analysis_type="Comprehensive Analysis",
        results=results,
        visualizations=visualizations
    )
    
    return {
        'results': results,
        'report': report_path,
        'visualizations': visualizations
    }
```

## Input Formats

### Variant Format
```python
variant = {
    "chromosome": "chr1",      # Include 'chr' prefix
    "position": 47239296,      # 1-based coordinate
    "ref": "C",                # Reference allele
    "alt": "CCGTTTCCTAACC",   # Alternate allele (can be insertion)
    "variant_id": "my_variant" # Unique identifier
}
```

### Supported Tissues
```python
TISSUES = [
    'lung', 'colon', 'liver', 'brain', 'breast',
    'prostate', 'pancreas', 'blood', 'lymphoid'
]
```

### Supported Genes
Major cancer genes are pre-configured:
```python
CANCER_GENES = [
    'MYC', 'EGFR', 'BRAF', 'KRAS', 'TP53', 'PTEN',
    'TAL1', 'TERT', 'PIK3CA', 'MET', 'ALK', 'ROS1'
]
```

## Output Structure

### Standard Response
```python
{
    "status": "success",
    "question": "original question",
    "gene": "MYC",
    "tissue": "lung",
    "analysis_results": {
        # Detailed analysis results
    },
    "report": "path/to/markdown/report.md",
    "visualizations": [
        "path/to/visualization1.png",
        "path/to/visualization2.png"
    ],
    "key_findings": [
        "Variant creates strong enhancer 500kb upstream",
        "Enhancer is tissue-specific to lung cells",
        "Predicted 5-fold increase in MYC expression"
    ],
    "clinical_relevance": "High - potential therapeutic target"
}
```

### Report Contents
Generated markdown reports include:
- Executive summary
- Key findings with data tables
- Embedded visualizations
- Clinical interpretation
- Therapeutic recommendations
- Methods description

## Advanced Features

### 1. Batch Processing
```python
# Analyze multiple variants efficiently
variants = [variant1, variant2, variant3, ...]
results = pipeline.find_convergent_mechanisms(
    patient_variants={"cohort": variants},
    target_genes=["MYC", "TERT", "TP53"],
    tissue="lung"
)
```

### 2. Patient Stratification
```python
# Group patients by regulatory mechanism
patient_groups = {
    "patient1": [variant1a, variant1b],
    "patient2": [variant2a, variant2b],
    "patient3": [variant3a, variant3b]
}

convergence = pipeline.find_convergent_mechanisms(
    patient_variants=patient_groups,
    target_genes=["MYC"],
    tissue="colon"
)
```

### 3. Custom Visualization
```python
# Create custom multi-panel figures
from alphagenome.visualization import plot_components

# Combine multiple outputs
fig = plot_components.plot(
    components=[rna_tracks, dnase_tracks, histone_tracks],
    interval=interval,
    annotations=[variant_annotations],
    title="Custom Analysis"
)
```

## Best Practices for AI Agents

1. **Question Parsing**:
   - Extract gene names (usually uppercase: EGFR, MYC)
   - Identify tissue types from context
   - Detect variant information if provided

2. **Error Handling**:
   ```python
   try:
       results = analyze_regulatory_cancer_mechanism(...)
   except Exception as e:
       return f"Analysis failed: {str(e)}"
   ```

3. **Performance**:
   - Limit to 10 variants per analysis for speed
   - Use 131kb windows for variant analysis
   - Cache results for repeated queries

4. **Interpretation**:
   - Focus on fold changes > 2 as significant
   - Highlight tissue-specific effects
   - Emphasize oncogene activation warnings

## Example AI Agent Implementation

```python
class CancerResearchAgent:
    def __init__(self, api_key):
        self.api_key = api_key
        self.pipeline = AlphaGenomeCancerPipeline(api_key)
        
    def answer_question(self, question):
        # Parse question
        gene = self.extract_gene(question)
        tissue = self.extract_tissue(question)
        
        # Determine analysis type
        if "enhancer" in question.lower():
            return self.analyze_enhancers(gene, tissue)
        elif "tissue" in question.lower() and "specific" in question.lower():
            return self.analyze_tissue_specificity(gene, tissue)
        elif "regulatory" in question.lower() or "landscape" in question.lower():
            return self.map_regulatory_landscape(gene, tissue)
        else:
            # Default to comprehensive analysis
            return analyze_regulatory_cancer_mechanism(
                question=question,
                gene=gene,
                tissue=tissue,
                api_key=self.api_key
            )
    
    def extract_gene(self, question):
        # Simple pattern matching for gene names
        import re
        genes = ['MYC', 'EGFR', 'BRAF', 'KRAS', 'TP53', 'TAL1', 'TERT']
        for gene in genes:
            if gene in question.upper():
                return gene
        return None
    
    def extract_tissue(self, question):
        # Extract tissue type
        tissues = {
            'lung': ['lung', 'pulmonary', 'nsclc'],
            'blood': ['blood', 'leukemia', 'lymphoma', 't-cell'],
            'brain': ['brain', 'glioma', 'glioblastoma'],
            'colon': ['colon', 'colorectal', 'crc']
        }
        
        question_lower = question.lower()
        for tissue, keywords in tissues.items():
            if any(kw in question_lower for kw in keywords):
                return tissue
        return 'blood'  # default
```

## Troubleshooting

1. **No results returned**:
   - Check gene name spelling
   - Verify tissue type is supported
   - Ensure variants are in correct format

2. **Visualization errors**:
   - Verify matplotlib is installed
   - Check output directory exists
   - Ensure sufficient memory for large intervals

3. **API errors**:
   - Verify API key is valid
   - Check internet connection
   - Respect rate limits

## Summary

The AlphaGenome pipeline enables AI agents to:
- Answer complex cancer biology questions
- Generate publication-quality visualizations
- Create comprehensive research reports
- Discover novel regulatory mechanisms
- Provide therapeutic recommendations

Focus on the non-coding genome where the answers to many cancer mysteries lie!