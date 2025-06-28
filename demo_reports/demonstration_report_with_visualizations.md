# AlphaGenome Cancer Analysis Report - Demonstration

**Analysis Type**: Combined Regulatory Analysis
**Generated**: 2025-06-28

---

## Executive Summary

This demonstration report shows the types of visualizations and insights that AlphaGenome can provide for cancer research. The analysis reveals how non-coding variants create new regulatory elements and alter gene expression in cancer.

## Key Findings

### 1. TAL1 De Novo Enhancer Creation

The 12bp insertion at chr1:47239296 creates a powerful new enhancer element:

- **3.5-fold increase** in TAL1 expression
- **New chromatin accessibility peak** at the insertion site
- **Strong H3K27ac signal** indicating active enhancer formation
- **Tissue-specific to blood cells** (T-cell lineage)

![TAL1 Variant Impact](demo_visualizations/TAL1_variant_impact_demo.png)

*Figure 1: The insertion creates a de novo enhancer. Red traces show the alternate allele creating new regulatory activity absent in the reference genome (grey). The orange dashed line marks the variant position.*

### 2. MYC Regulatory Landscape

Analysis of the MYC locus reveals multiple distal enhancers:

- **3 active enhancers** identified at -25kb, -15kb, and +20kb from MYC
- **Strong promoter activity** with H3K4me3 marking
- **Open chromatin** throughout regulatory regions
- **Tissue-specific enhancer usage** in lung tissue

![MYC Regulatory Landscape](demo_visualizations/MYC_regulatory_landscape_demo.png)

*Figure 2: Complete regulatory landscape of MYC showing enhancers (H3K27ac peaks), promoter activity (H3K4me3), chromatin accessibility (DNase), and gene expression (RNA-seq).*

## Interpretation

### TAL1 Activation Mechanism
The TAL1 insertion demonstrates a classic example of oncogene activation through regulatory hijacking. The inserted sequence contains binding motifs for blood-specific transcription factors (RUNX1, TAL1, GATA), creating a powerful enhancer that inappropriately activates TAL1 in T-cells where it should be silent.

### MYC Regulation
The MYC analysis reveals the complexity of oncogene regulation, with multiple enhancers working in concert. The identified enhancers represent potential therapeutic targets—blocking these elements could reduce MYC expression in cancer cells.

## Clinical Implications

1. **Diagnostic Value**: Non-coding variants like the TAL1 insertion should be included in cancer genomic panels
2. **Therapeutic Targets**: The identified enhancers can be targeted with CRISPR or small molecules
3. **Patient Stratification**: Patients can be grouped by their regulatory mechanisms for precision therapy

## Methods

This analysis used AlphaGenome to predict the regulatory effects of DNA sequence variants. The model analyzes:
- Gene expression changes (RNA-seq predictions)
- Chromatin accessibility alterations (DNase-seq, ATAC-seq)
- Histone modification patterns (ChIP-seq for multiple marks)
- 3D chromatin interactions
- Tissue-specific regulatory activity

AlphaGenome's predictions are based on deep learning models trained on thousands of functional genomics experiments across hundreds of cell types and tissues.

## Recommendations

1. **Validate TAL1 enhancer** with CRISPR deletion in T-ALL cell lines
2. **Screen for similar insertions** in other T-ALL patients
3. **Test enhancer-blocking strategies** for MYC-driven cancers
4. **Expand analysis** to other known oncogenes

---

*This demonstration report showcases AlphaGenome's capability to discover and visualize novel regulatory mechanisms in cancer.*
