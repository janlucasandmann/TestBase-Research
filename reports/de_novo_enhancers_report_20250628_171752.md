# AlphaGenome Cancer Analysis Report

**Analysis Type**: De Novo Enhancers
**Generated**: 2025-06-28 17:17:52

---

## De Novo Enhancer Discovery

**Tissue**: blood
**Variants Analyzed**: 1
**De Novo Enhancers Found**: 1

### Discovered Enhancers

| Variant | Location | Enhancer Score | Affected Genes |
|---------|----------|----------------|----------------|
| TAL1_enhancer_insertion | chr1:47239296 | 0.950 | TAL1 |

⚠️ **Warning**: De novo enhancers activating oncogenes detected!


## Visualizations

### TAL1 enhancer insertion chr1 47239296

![TAL1 enhancer insertion chr1 47239296](visualizations/TAL1_enhancer_insertion_chr1_47239296.png)


## Interpretation

The analysis identified variants that create new enhancer elements. These de novo enhancers can lead to inappropriate gene activation, particularly concerning when they affect oncogenes. Such variants represent a mechanism for cancer development through regulatory disruption.

## Methods

This analysis was performed using AlphaGenome, a deep learning model that predicts the effects of DNA sequence variants on gene expression and chromatin state. The model analyzes sequences up to 1Mb in length and provides predictions for:

- Gene expression (RNA-seq)
- Chromatin accessibility (DNase-seq, ATAC-seq)
- Histone modifications (ChIP-seq)
- Transcription factor binding
- Splicing patterns
- 3D chromatin interactions
