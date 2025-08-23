"""Ontology mapping for tissue and cell types to AlphaGenome track IDs."""

from typing import Dict, List, Optional, Set


class OntologyMapper:
    """Maps human-readable tissue/cell types to API track identifiers."""
    
    def __init__(self):
        """Initialize with default mappings."""
        self.tissue_to_tracks: Dict[str, List[str]] = {
            "hematopoietic": [
                "dnase_CD14_monocyte",
                "dnase_CD4_T_cell",
                "dnase_CD8_T_cell",
                "cage_CD14_monocyte",
                "cage_CD4_T_cell",
                "h3k27ac_CD14_monocyte",
                "h3k27ac_CD4_T_cell",
                "atac_CD4_T_cell",
                "atac_CD8_T_cell"
            ],
            "liver": [
                "dnase_liver",
                "cage_liver",
                "h3k27ac_liver",
                "h3k4me3_liver",
                "atac_liver"
            ],
            "brain": [
                "dnase_brain",
                "cage_brain_frontal",
                "cage_brain_hippocampus",
                "h3k27ac_brain",
                "h3k4me3_brain",
                "atac_brain"
            ],
            "lung": [
                "dnase_lung",
                "cage_lung",
                "h3k27ac_lung",
                "h3k4me3_lung",
                "atac_lung"
            ],
            "heart": [
                "dnase_heart_left_ventricle",
                "dnase_heart_right_atrium",
                "cage_heart",
                "h3k27ac_heart",
                "atac_heart"
            ],
            "kidney": [
                "dnase_kidney",
                "cage_kidney",
                "h3k27ac_kidney",
                "atac_kidney"
            ],
            "pancreas": [
                "dnase_pancreas",
                "cage_pancreas",
                "h3k27ac_pancreas",
                "atac_pancreas"
            ]
        }
        
        self.modality_prefixes = {
            "dnase": "ATAC_DNASE",
            "atac": "ATAC_DNASE",
            "cage": "TSS_CAGE",
            "h3k27ac": "HISTONE",
            "h3k4me3": "HISTONE",
            "h3k4me1": "HISTONE",
            "h3k27me3": "HISTONE",
            "h3k9me3": "HISTONE",
            "h3k36me3": "HISTONE",
            "ctcf": "TF_BIND",
            "pol2": "TF_BIND",
            "cebpb": "TF_BIND",
            "jun": "TF_BIND",
            "fos": "TF_BIND"
        }
        
        self.ontology_ids: Dict[str, str] = {
            "CD14_monocyte": "CL:0000235",
            "CD4_T_cell": "CL:0000624",
            "CD8_T_cell": "CL:0000625",
            "liver": "UBERON:0002107",
            "brain": "UBERON:0000955",
            "lung": "UBERON:0002048",
            "heart": "UBERON:0000948",
            "kidney": "UBERON:0002113",
            "pancreas": "UBERON:0001264"
        }
    
    def get_tracks_for_tissue(
        self, 
        tissue: str,
        modalities: Optional[Set[str]] = None
    ) -> List[str]:
        """Get track IDs for a given tissue.
        
        Args:
            tissue: Human-readable tissue name
            modalities: Optional set of modality types to filter
            
        Returns:
            List of track IDs
        """
        tissue_lower = tissue.lower()
        tracks = self.tissue_to_tracks.get(tissue_lower, [])
        
        if modalities:
            modality_lower = {m.lower() for m in modalities}
            tracks = [
                t for t in tracks 
                if any(t.startswith(m) for m in modality_lower)
            ]
        
        return tracks
    
    def get_modality_type(self, track_id: str) -> Optional[str]:
        """Determine modality type from track ID.
        
        Args:
            track_id: AlphaGenome track identifier
            
        Returns:
            Modality type or None
        """
        track_lower = track_id.lower()
        for prefix, modality in self.modality_prefixes.items():
            if track_lower.startswith(prefix):
                return modality
        return None
    
    def get_ontology_id(self, term: str) -> Optional[str]:
        """Get ontology ID for a tissue or cell type.
        
        Args:
            term: Tissue or cell type name
            
        Returns:
            Ontology ID or None
        """
        return self.ontology_ids.get(term, None)
    
    def add_custom_mapping(
        self,
        tissue: str,
        tracks: List[str],
        ontology_id: Optional[str] = None
    ) -> None:
        """Add custom tissue-to-track mapping.
        
        Args:
            tissue: Tissue name
            tracks: List of track IDs
            ontology_id: Optional ontology identifier
        """
        self.tissue_to_tracks[tissue.lower()] = tracks
        if ontology_id:
            self.ontology_ids[tissue] = ontology_id


ontology_mapper = OntologyMapper()