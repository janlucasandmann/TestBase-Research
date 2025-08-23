# 🎯 Recommended Research Questions Based on cBioPortal Data

**Generated from TCGA Pan-Cancer Atlas mutation analysis**  
**Date**: August 11, 2025

Based on our analysis of cBioPortal mutation data, here are the **top research questions** with the richest available variant data for AlphaGenome analysis:

---

## 🔴 **HIGHEST PRIORITY** (300+ mutations available)

### 1. How do PIK3CA mutations create de novo enhancers in breast cancer?
- **Gene**: PIK3CA  
- **Cancer Type**: Breast cancer
- **Mutations Available**: 387 mutations in TCGA dataset
- **Study ID**: `brca_tcga_pan_can_atlas_2018`
- **Why this is excellent**: PIK3CA is the most frequently mutated gene in breast cancer, giving us abundant data for regulatory analysis

### 2. How do TP53 mutations affect tissue-specific regulatory networks in breast cancer?
- **Gene**: TP53
- **Cancer Type**: Breast cancer  
- **Mutations Available**: 353 mutations in TCGA dataset
- **Study ID**: `brca_tcga_pan_can_atlas_2018`
- **Why this is excellent**: TP53 is the "guardian of the genome" - understanding its regulatory effects is crucial

---

## 🟡 **HIGH PRIORITY** (100+ mutations available)

### 3. What long-range chromatin interactions are disrupted by GATA3 variants in breast cancer?
- **Gene**: GATA3
- **Cancer Type**: Breast cancer
- **Mutations Available**: 130 mutations in TCGA dataset  
- **Study ID**: `brca_tcga_pan_can_atlas_2018`
- **Why this is excellent**: GATA3 is a transcription factor - perfect for regulatory analysis

### 4. How do KRAS mutations create tissue-specific enhancers in lung cancer?
- **Gene**: KRAS
- **Cancer Type**: Lung adenocarcinoma
- **Mutations Available**: ~200+ expected mutations
- **Study ID**: `luad_tcga_pan_can_atlas_2018`
- **Why this is excellent**: KRAS is highly mutated in lung cancer and drives oncogenesis

### 5. Which regulatory elements are altered by APC mutations in colorectal cancer?
- **Gene**: APC
- **Cancer Type**: Colorectal cancer
- **Mutations Available**: ~300+ expected mutations
- **Study ID**: `coadread_tcga_pan_can_atlas_2018`
- **Why this is excellent**: APC is the most commonly mutated gene in colorectal cancer

---

## 🟢 **GOOD PRIORITY** (50+ mutations available)

### 6. How do PTEN mutations affect enhancer landscapes in breast cancer?
- **Gene**: PTEN
- **Cancer Type**: Breast cancer
- **Mutations Available**: 64 mutations in TCGA dataset
- **Study ID**: `brca_tcga_pan_can_atlas_2018`
- **Why this is good**: PTEN is a key tumor suppressor with known regulatory roles

### 7. What splicing networks are disrupted by BRCA1 mutations?
- **Gene**: BRCA1
- **Cancer Type**: Breast cancer
- **Mutations Available**: 27 mutations in TCGA dataset
- **Study ID**: `brca_tcga_pan_can_atlas_2018`
- **Why this is good**: BRCA1 has important regulatory functions beyond DNA repair

---

## 🔬 **Implementation Recommendations**

### **Start with #1 or #2** for maximum impact:
- Both PIK3CA and TP53 have 300+ mutations available
- Breast cancer data is well-curated in TCGA
- These genes have known regulatory importance

### **Perfect for AlphaGenome analysis**:
- All questions focus on **regulatory mechanisms** (not just coding effects)
- Questions target **tissue-specific effects** (perfect for AlphaGenome's capabilities)
- Rich variant data ensures robust statistical analysis

### **Next Steps**:
1. **Choose PIK3CA in breast cancer** (387 mutations - highest data availability)
2. **Adapt the MGMT pipeline** for PIK3CA analysis
3. **Focus on enhancer discovery** (PIK3CA mutations likely create new regulatory elements)
4. **Compare tissue specificity** (breast vs other tissues)

---

## 📊 **Why These Questions Work Better Than MGMT**

| Gene | Cancer | Mutations | vs MGMT |
|------|---------|-----------|---------|
| **PIK3CA** | Breast | **387** | 387x more data |
| **TP53** | Breast | **353** | 353x more data |  
| **GATA3** | Breast | **130** | 130x more data |
| MGMT | Glioblastoma | 1 | Baseline |

**The data availability difference is dramatic** - we'll have hundreds of variants to analyze instead of just 1!

---

## 🚀 **Recommended Next Action**

**Use PIK3CA in breast cancer** as our next research question:
- Modify `mgmt_research_analysis.py` → `pik3ca_research_analysis.py`
- Change study ID to `brca_tcga_pan_can_atlas_2018`
- Focus on breast tissue specificity
- Analyze how PIK3CA mutations create enhancers that drive breast cancer

This will demonstrate the full power of our real clinical data pipeline with abundant variant data!