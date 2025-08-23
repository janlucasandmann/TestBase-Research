"""
Advanced Regulatory Assessment Framework

Instead of arbitrary numeric scores, this provides biologically meaningful
assessments with multiple dimensions of evidence and clear interpretation.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import numpy as np


class RegulatoryClass(str, Enum):
    """Biologically meaningful regulatory classifications."""
    ACTIVE_ENHANCER = "active_enhancer"      # H3K27ac+, H3K4me1+, accessible
    PRIMED_ENHANCER = "primed_enhancer"      # H3K4me1+, accessible, H3K27ac-
    WEAK_ENHANCER = "weak_enhancer"          # Some enhancer signatures
    PROMOTER_LIKE = "promoter_like"          # H3K4me3+, accessible
    GENE_BODY = "gene_body"                  # H3K36me3+, transcribed
    HETEROCHROMATIN = "heterochromatin"      # H3K27me3+, H3K9me3+
    QUIESCENT = "quiescent"                  # Low signals across marks
    AMBIGUOUS = "ambiguous"                  # Mixed or unclear signals
    NOT_APPLICABLE = "not_applicable"        # Gene-proximal, can't assess


class EvidenceStrength(str, Enum):
    """Clear evidence strength categories."""
    STRONG = "strong"        # Multiple independent lines of evidence
    MODERATE = "moderate"    # Some supporting evidence
    WEAK = "weak"           # Minimal evidence
    CONFLICTING = "conflicting"  # Evidence points in different directions
    INSUFFICIENT = "insufficient"  # Not enough data


@dataclass
class BiologicalEvidence:
    """Structure for organizing biological evidence."""
    chromatin_accessibility: float = 0.0
    active_marks: Dict[str, float] = None
    repressive_marks: Dict[str, float] = None
    transcription: float = 0.0
    conservation_score: Optional[float] = None
    tissue_specificity: Optional[float] = None
    
    def __post_init__(self):
        if self.active_marks is None:
            self.active_marks = {}
        if self.repressive_marks is None:
            self.repressive_marks = {}


@dataclass
class RegulatoryAssessment:
    """Comprehensive regulatory assessment replacing simple scores."""
    
    # Primary classification
    regulatory_class: RegulatoryClass
    evidence_strength: EvidenceStrength
    confidence_level: str  # High/Medium/Low with specific rationale
    
    # Multi-dimensional evidence
    biological_evidence: BiologicalEvidence
    
    # Interpretation
    biological_interpretation: str
    functional_prediction: str
    target_genes: List[str]
    
    # Context
    genomic_context: str
    tissue_context: str
    comparative_analysis: str
    
    # Actionable insights
    follow_up_experiments: List[str]
    clinical_relevance: str
    literature_support: List[str]
    
    # Quality metrics
    data_quality_flags: List[str]
    limitations: List[str]


class RegulatoryAssessmentEngine:
    """
    Advanced assessment engine that provides biological insight
    rather than arbitrary numeric scores.
    """
    
    def __init__(self):
        # Thresholds based on ENCODE percentiles and literature
        self.accessibility_thresholds = {
            'strong': 0.1,    # Top 10% of accessible regions
            'moderate': 0.05, # Top 20%
            'weak': 0.01      # Top 50%
        }
        
        self.histone_thresholds = {
            'H3K27ac': {'strong': 0.2, 'moderate': 0.1, 'weak': 0.05},
            'H3K4me1': {'strong': 0.1, 'moderate': 0.05, 'weak': 0.02},
            'H3K4me3': {'strong': 0.15, 'moderate': 0.1, 'weak': 0.05},
            'H3K36me3': {'strong': 0.1, 'moderate': 0.05, 'weak': 0.02},
            'H3K27me3': {'strong': 0.1, 'moderate': 0.05, 'weak': 0.02}
        }
    
    def assess_variant(
        self, 
        alphagenome_data: Dict,
        genomic_context: Dict,
        variant_id: str
    ) -> RegulatoryAssessment:
        """
        Perform comprehensive regulatory assessment.
        
        Args:
            alphagenome_data: AlphaGenome API results
            genomic_context: Genomic location context
            variant_id: Variant identifier
            
        Returns:
            Comprehensive RegulatoryAssessment
        """
        
        # Extract biological evidence
        bio_evidence = self._extract_biological_evidence(alphagenome_data)
        
        # Classify regulatory potential
        reg_class = self._classify_regulatory_element(bio_evidence, genomic_context)
        
        # Assess evidence strength
        evidence_strength = self._assess_evidence_strength(bio_evidence, reg_class)
        
        # Determine confidence with rationale
        confidence, confidence_rationale = self._determine_confidence(
            bio_evidence, reg_class, genomic_context
        )
        
        # Generate biological interpretation
        interpretation = self._generate_biological_interpretation(
            reg_class, bio_evidence, genomic_context
        )
        
        # Predict functional consequences
        functional_pred = self._predict_functional_consequences(
            reg_class, bio_evidence, genomic_context
        )
        
        # Identify potential target genes
        target_genes = self._identify_target_genes(genomic_context, reg_class)
        
        # Generate comparative analysis
        comparative = self._generate_comparative_analysis(
            bio_evidence, reg_class, genomic_context
        )
        
        # Suggest follow-up experiments
        follow_ups = self._suggest_followup_experiments(reg_class, evidence_strength)
        
        # Assess clinical relevance
        clinical_rel = self._assess_clinical_relevance(
            reg_class, genomic_context, variant_id
        )
        
        # Quality control assessment
        quality_flags = self._assess_data_quality(alphagenome_data)
        limitations = self._identify_limitations(alphagenome_data, genomic_context)
        
        return RegulatoryAssessment(
            regulatory_class=reg_class,
            evidence_strength=evidence_strength,
            confidence_level=f"{confidence} - {confidence_rationale}",
            biological_evidence=bio_evidence,
            biological_interpretation=interpretation,
            functional_prediction=functional_pred,
            target_genes=target_genes,
            genomic_context=self._format_genomic_context(genomic_context),
            tissue_context=genomic_context.get('tissue', 'Unknown'),
            comparative_analysis=comparative,
            follow_up_experiments=follow_ups,
            clinical_relevance=clinical_rel,
            literature_support=[],  # Would populate from literature search
            data_quality_flags=quality_flags,
            limitations=limitations
        )
    
    def _extract_biological_evidence(self, alphagenome_data: Dict) -> BiologicalEvidence:
        """Extract and structure biological evidence from AlphaGenome data."""
        summary = alphagenome_data.get('summary', {})
        
        # Accessibility
        accessibility = summary.get('dnase', {}).get('max_increase', 0)
        
        # Active histone marks
        histone_marks = summary.get('chip_histone', {}).get('marks', {})
        active_marks = {
            'H3K27ac': histone_marks.get('H3K27ac', {}).get('max_increase', 0),
            'H3K4me1': histone_marks.get('H3K4me1', {}).get('max_increase', 0),
            'H3K4me3': histone_marks.get('H3K4me3', {}).get('max_increase', 0),
            'H3K36me3': histone_marks.get('H3K36me3', {}).get('max_increase', 0)
        }
        
        # Repressive marks (if available)
        repressive_marks = {
            'H3K27me3': histone_marks.get('H3K27me3', {}).get('max_increase', 0),
            'H3K9me3': histone_marks.get('H3K9me3', {}).get('max_increase', 0)
        }
        
        # Transcription
        transcription = summary.get('rna_seq', {}).get('max_increase', 0)
        
        return BiologicalEvidence(
            chromatin_accessibility=accessibility,
            active_marks=active_marks,
            repressive_marks=repressive_marks,
            transcription=transcription
        )
    
    def _classify_regulatory_element(
        self, 
        bio_evidence: BiologicalEvidence,
        genomic_context: Dict
    ) -> RegulatoryClass:
        """Classify the type of regulatory element based on chromatin signatures."""
        
        # Pre-filter: gene-proximal regions
        if genomic_context.get('is_exon', False) or genomic_context.get('is_coding', False):
            return RegulatoryClass.NOT_APPLICABLE
        
        if genomic_context.get('distance_to_tss', float('inf')) < 2000:
            return RegulatoryClass.NOT_APPLICABLE
        
        # Get mark strengths
        h3k27ac = bio_evidence.active_marks.get('H3K27ac', 0)
        h3k4me1 = bio_evidence.active_marks.get('H3K4me1', 0)
        h3k4me3 = bio_evidence.active_marks.get('H3K4me3', 0)
        h3k36me3 = bio_evidence.active_marks.get('H3K36me3', 0)
        h3k27me3 = bio_evidence.repressive_marks.get('H3K27me3', 0)
        accessibility = bio_evidence.chromatin_accessibility
        
        # Classification logic based on chromatin state literature
        
        # Active enhancer: H3K27ac+ H3K4me1+ accessible
        if (h3k27ac >= self.histone_thresholds['H3K27ac']['moderate'] and
            h3k4me1 >= self.histone_thresholds['H3K4me1']['moderate'] and
            accessibility >= self.accessibility_thresholds['moderate']):
            return RegulatoryClass.ACTIVE_ENHANCER
        
        # Primed enhancer: H3K4me1+ accessible but no H3K27ac
        if (h3k4me1 >= self.histone_thresholds['H3K4me1']['moderate'] and
            accessibility >= self.accessibility_thresholds['moderate'] and
            h3k27ac < self.histone_thresholds['H3K27ac']['weak']):
            return RegulatoryClass.PRIMED_ENHANCER
        
        # Promoter-like: H3K4me3+ accessible
        if (h3k4me3 >= self.histone_thresholds['H3K4me3']['moderate'] and
            accessibility >= self.accessibility_thresholds['moderate']):
            return RegulatoryClass.PROMOTER_LIKE
        
        # Gene body: H3K36me3+ transcribed
        if (h3k36me3 >= self.histone_thresholds['H3K36me3']['moderate'] and
            bio_evidence.transcription > 0.001):
            return RegulatoryClass.GENE_BODY
        
        # Heterochromatin: H3K27me3+
        if h3k27me3 >= self.histone_thresholds['H3K27me3']['moderate']:
            return RegulatoryClass.HETEROCHROMATIN
        
        # Weak enhancer: some enhancer-like signals but below thresholds
        if (h3k4me1 >= self.histone_thresholds['H3K4me1']['weak'] or
            h3k27ac >= self.histone_thresholds['H3K27ac']['weak'] or
            accessibility >= self.accessibility_thresholds['weak']):
            return RegulatoryClass.WEAK_ENHANCER
        
        # Mixed signals
        if sum([h3k27ac, h3k4me1, h3k4me3, accessibility]) > 0.02:
            return RegulatoryClass.AMBIGUOUS
        
        # Low signals across all marks
        return RegulatoryClass.QUIESCENT
    
    def _assess_evidence_strength(
        self, 
        bio_evidence: BiologicalEvidence,
        reg_class: RegulatoryClass
    ) -> EvidenceStrength:
        """Assess the strength of evidence for the classification."""
        
        if reg_class == RegulatoryClass.NOT_APPLICABLE:
            return EvidenceStrength.STRONG  # Clear exclusion criteria
        
        # Count number of supporting marks above threshold
        supporting_evidence = 0
        conflicting_evidence = 0
        
        h3k27ac = bio_evidence.active_marks.get('H3K27ac', 0)
        h3k4me1 = bio_evidence.active_marks.get('H3K4me1', 0)
        h3k4me3 = bio_evidence.active_marks.get('H3K4me3', 0)
        accessibility = bio_evidence.chromatin_accessibility
        
        if reg_class in [RegulatoryClass.ACTIVE_ENHANCER, RegulatoryClass.PRIMED_ENHANCER]:
            if h3k4me1 >= self.histone_thresholds['H3K4me1']['moderate']:
                supporting_evidence += 1
            if accessibility >= self.accessibility_thresholds['moderate']:
                supporting_evidence += 1
            if reg_class == RegulatoryClass.ACTIVE_ENHANCER:
                if h3k27ac >= self.histone_thresholds['H3K27ac']['moderate']:
                    supporting_evidence += 1
            
            # Conflicting evidence: high H3K4me3 suggests promoter
            if h3k4me3 >= self.histone_thresholds['H3K4me3']['moderate']:
                conflicting_evidence += 1
        
        if conflicting_evidence > 0:
            return EvidenceStrength.CONFLICTING
        elif supporting_evidence >= 3:
            return EvidenceStrength.STRONG
        elif supporting_evidence >= 2:
            return EvidenceStrength.MODERATE
        elif supporting_evidence >= 1:
            return EvidenceStrength.WEAK
        else:
            return EvidenceStrength.INSUFFICIENT
    
    def _determine_confidence(
        self, 
        bio_evidence: BiologicalEvidence,
        reg_class: RegulatoryClass,
        genomic_context: Dict
    ) -> Tuple[str, str]:
        """Determine confidence level with specific rationale."""
        
        if reg_class == RegulatoryClass.NOT_APPLICABLE:
            return "High", "Coding variant in exon - regulatory assessment not applicable"
        
        # Quality factors
        tissue_matched = genomic_context.get('tissue_matched', False)
        replicate_count = genomic_context.get('replicate_count', 1)
        
        rationale_parts = []
        confidence_score = 0
        
        # Evidence strength contributes to confidence
        evidence_strength = self._assess_evidence_strength(bio_evidence, reg_class)
        if evidence_strength == EvidenceStrength.STRONG:
            confidence_score += 3
            rationale_parts.append("strong multi-mark evidence")
        elif evidence_strength == EvidenceStrength.MODERATE:
            confidence_score += 2
            rationale_parts.append("moderate evidence")
        elif evidence_strength == EvidenceStrength.WEAK:
            confidence_score += 1
            rationale_parts.append("limited evidence")
        else:
            confidence_score += 0
            rationale_parts.append("insufficient evidence")
        
        # Data quality factors
        if tissue_matched:
            confidence_score += 1
            rationale_parts.append("tissue-matched data")
        else:
            rationale_parts.append("no tissue-specific data")
        
        if replicate_count >= 2:
            confidence_score += 1
            rationale_parts.append("replicated")
        else:
            rationale_parts.append("single replicate")
        
        # Determine final confidence
        if confidence_score >= 4:
            confidence = "High"
        elif confidence_score >= 2:
            confidence = "Medium"
        else:
            confidence = "Low"
        
        rationale = "; ".join(rationale_parts)
        return confidence, rationale
    
    def _generate_biological_interpretation(
        self, 
        reg_class: RegulatoryClass,
        bio_evidence: BiologicalEvidence,
        genomic_context: Dict
    ) -> str:
        """Generate biological interpretation of the findings."""
        
        interpretations = {
            RegulatoryClass.NOT_APPLICABLE: 
                "This variant is located in a coding region where enhancer assessment is not applicable. "
                "Observed chromatin signals likely reflect gene body activity rather than regulatory element creation.",
            
            RegulatoryClass.ACTIVE_ENHANCER:
                "Strong evidence for an active enhancer element. The presence of H3K27ac and H3K4me1 marks "
                "along with chromatin accessibility suggests this region can actively regulate gene expression.",
            
            RegulatoryClass.PRIMED_ENHANCER:
                "Evidence for a primed enhancer element. H3K4me1 marking and chromatin accessibility indicate "
                "enhancer potential, but lack of H3K27ac suggests it may require additional signals for activation.",
            
            RegulatoryClass.WEAK_ENHANCER:
                "Weak evidence for enhancer activity. Some enhancer-associated marks are present but below "
                "typical thresholds for strong regulatory elements.",
            
            RegulatoryClass.PROMOTER_LIKE:
                "Chromatin signature resembles a promoter rather than an enhancer, with H3K4me3 enrichment "
                "and accessibility typical of transcription start site regions.",
            
            RegulatoryClass.GENE_BODY:
                "Chromatin signature indicates gene body region with active transcription (H3K36me3). "
                "RNA signal likely reflects mRNA production rather than enhancer RNA.",
            
            RegulatoryClass.QUIESCENT:
                "No evidence for regulatory activity. Low levels of chromatin marks and accessibility "
                "suggest this region is transcriptionally inactive.",
            
            RegulatoryClass.AMBIGUOUS:
                "Mixed chromatin signals make classification unclear. Additional data or functional "
                "validation would be needed to determine regulatory potential."
        }
        
        base_interpretation = interpretations.get(reg_class, "Unknown regulatory classification.")
        
        # Add context-specific details
        if genomic_context.get('gene'):
            gene = genomic_context['gene']
            if reg_class == RegulatoryClass.NOT_APPLICABLE:
                base_interpretation += f" For {gene} coding variants, focus should be on protein-level effects."
        
        return base_interpretation
    
    def _predict_functional_consequences(
        self,
        reg_class: RegulatoryClass,
        bio_evidence: BiologicalEvidence, 
        genomic_context: Dict
    ) -> str:
        """Predict functional consequences of the variant."""
        
        if reg_class == RegulatoryClass.NOT_APPLICABLE:
            return "Functional effects likely involve protein coding changes rather than gene regulation."
        
        if reg_class in [RegulatoryClass.ACTIVE_ENHANCER, RegulatoryClass.PRIMED_ENHANCER]:
            strength = "strong" if reg_class == RegulatoryClass.ACTIVE_ENHANCER else "moderate"
            return f"Predicted to create or strengthen a regulatory element with {strength} enhancer activity. " \
                   f"May affect expression of nearby genes in tissue-specific manner."
        
        if reg_class == RegulatoryClass.WEAK_ENHANCER:
            return "May have subtle regulatory effects. Likely requires specific cellular contexts for activity."
        
        return "Minimal predicted functional consequences for gene regulation."
    
    def _identify_target_genes(self, genomic_context: Dict, reg_class: RegulatoryClass) -> List[str]:
        """Identify potential target genes for regulatory elements."""
        
        if reg_class == RegulatoryClass.NOT_APPLICABLE:
            return [genomic_context.get('gene', 'Unknown')]
        
        # For now, return the local gene - would enhance with Hi-C/eQTL data
        target_genes = []
        if genomic_context.get('gene'):
            target_genes.append(genomic_context['gene'])
        
        return target_genes
    
    def _generate_comparative_analysis(
        self,
        bio_evidence: BiologicalEvidence,
        reg_class: RegulatoryClass,
        genomic_context: Dict
    ) -> str:
        """Generate comparative analysis context."""
        
        if reg_class == RegulatoryClass.NOT_APPLICABLE:
            return "Not applicable for coding variants. Compare with other coding mutations in the same gene."
        
        accessibility = bio_evidence.chromatin_accessibility
        if accessibility > 0.1:
            return "Chromatin accessibility is in top 10% of genomic regions, suggesting high regulatory potential."
        elif accessibility > 0.05:
            return "Moderate chromatin accessibility compared to genome background."
        else:
            return "Below-average chromatin accessibility compared to known regulatory elements."
    
    def _suggest_followup_experiments(
        self, 
        reg_class: RegulatoryClass,
        evidence_strength: EvidenceStrength
    ) -> List[str]:
        """Suggest appropriate follow-up experiments."""
        
        experiments = []
        
        if reg_class == RegulatoryClass.NOT_APPLICABLE:
            experiments.extend([
                "Functional protein assays for coding variant effects",
                "Structural modeling of protein changes",
                "Cell viability/proliferation assays"
            ])
        
        elif reg_class in [RegulatoryClass.ACTIVE_ENHANCER, RegulatoryClass.PRIMED_ENHANCER]:
            experiments.extend([
                "MPRA (Massively Parallel Reporter Assay) to test enhancer activity",
                "CRISPRi/CRISPRa at the candidate enhancer",
                "4C-seq or Hi-C to identify target genes",
                "CAGE-seq to detect enhancer RNA"
            ])
            
            if evidence_strength in [EvidenceStrength.WEAK, EvidenceStrength.INSUFFICIENT]:
                experiments.append("Higher resolution ChIP-seq in relevant cell types")
        
        elif reg_class == RegulatoryClass.WEAK_ENHANCER:
            experiments.extend([
                "Luciferase reporter assays",
                "Cell-type specific ChIP-seq",
                "ATAC-seq in multiple conditions"
            ])
        
        else:
            experiments.append("No specific regulatory experiments recommended")
        
        return experiments
    
    def _assess_clinical_relevance(
        self,
        reg_class: RegulatoryClass,
        genomic_context: Dict,
        variant_id: str
    ) -> str:
        """Assess potential clinical relevance."""
        
        gene = genomic_context.get('gene', 'Unknown')
        
        if reg_class == RegulatoryClass.NOT_APPLICABLE:
            if gene == 'KRAS':
                return f"High clinical relevance - {gene} coding variants are established oncogenic drivers " \
                       f"with therapeutic implications (KRAS inhibitors, pathway targeting)."
            else:
                return f"Clinical relevance depends on {gene} coding variant effects."
        
        elif reg_class in [RegulatoryClass.ACTIVE_ENHANCER, RegulatoryClass.PRIMED_ENHANCER]:
            return f"Potential clinical relevance if regulatory effects on {gene} or nearby genes " \
                   f"contribute to disease phenotype. Requires functional validation."
        
        else:
            return "Limited clinical relevance expected for regulatory effects."
    
    def _assess_data_quality(self, alphagenome_data: Dict) -> List[str]:
        """Assess data quality and flag potential issues."""
        flags = []
        
        # Add quality assessment based on AlphaGenome data
        summary = alphagenome_data.get('summary', {})
        
        if not summary.get('chip_histone', {}).get('marks'):
            flags.append("Limited histone mark data")
        
        if not summary.get('dnase'):
            flags.append("No DNase accessibility data")
        
        return flags
    
    def _identify_limitations(self, alphagenome_data: Dict, genomic_context: Dict) -> List[str]:
        """Identify limitations in the analysis."""
        limitations = [
            "Analysis based on population-level epigenomic data",
            "Cell-type specificity not fully captured",
            "No allele-specific analysis performed",
            "Long-range interactions not assessed",
            "No functional validation performed"
        ]
        
        if not genomic_context.get('tissue_matched', True):
            limitations.append("No tissue-matched epigenomic data available")
        
        return limitations
    
    def _format_genomic_context(self, genomic_context: Dict) -> str:
        """Format genomic context information."""
        parts = []
        
        if genomic_context.get('chromosome'):
            parts.append(f"Chromosome: {genomic_context['chromosome']}")
        
        if genomic_context.get('position'):
            parts.append(f"Position: {genomic_context['position']}")
        
        if genomic_context.get('gene'):
            parts.append(f"Gene: {genomic_context['gene']}")
        
        if genomic_context.get('region_type'):
            parts.append(f"Region: {genomic_context['region_type']}")
        
        return " | ".join(parts)