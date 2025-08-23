"""Core data models for TestBase Research."""

from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Set

from pydantic import BaseModel, Field, field_validator


class Assembly(str, Enum):
    """Genome assembly versions."""
    HG19 = "hg19"
    HG38 = "hg38"


class Variant(BaseModel):
    """Genomic variant representation."""
    chrom: str = Field(..., description="Chromosome (e.g., 'chr1', '1')")
    pos: int = Field(..., ge=1, description="1-based genomic position")
    ref: str = Field(..., min_length=1, description="Reference allele")
    alt: str = Field(..., min_length=1, description="Alternative allele")
    assembly: Assembly = Field(Assembly.HG38, description="Genome assembly")
    
    @field_validator("chrom")
    def normalize_chrom(cls, v: str) -> str:
        """Ensure chromosome has 'chr' prefix."""
        if not v.startswith("chr"):
            return f"chr{v}"
        return v
    
    def to_string(self) -> str:
        """Format as chr:pos:ref>alt."""
        return f"{self.chrom}:{self.pos}:{self.ref}>{self.alt}"


class GenomicInterval(BaseModel):
    """Genomic interval/region."""
    chrom: str = Field(..., description="Chromosome")
    start: int = Field(..., ge=0, description="0-based start position")
    end: int = Field(..., gt=0, description="0-based end position (exclusive)")
    assembly: Assembly = Field(Assembly.HG38, description="Genome assembly")
    
    @field_validator("chrom")
    def normalize_chrom(cls, v: str) -> str:
        """Ensure chromosome has 'chr' prefix."""
        if not v.startswith("chr"):
            return f"chr{v}"
        return v
    
    @field_validator("end")
    def validate_interval(cls, v: int, info) -> int:
        """Ensure end > start."""
        if hasattr(info, 'data') and 'start' in info.data and v <= info.data['start']:
            raise ValueError(f"end ({v}) must be greater than start ({info.data['start']})")
        return v
    
    @property
    def length(self) -> int:
        """Get interval length."""
        return self.end - self.start
    
    def to_string(self) -> str:
        """Format as chr:start-end."""
        return f"{self.chrom}:{self.start}-{self.end}"


class Context(BaseModel):
    """Biological context for predictions."""
    tissue: Optional[str] = Field(None, description="Tissue type")
    cell_type: Optional[str] = Field(None, description="Cell type")
    ontology_ids: List[str] = Field(default_factory=list, description="Ontology identifiers")
    
    def is_empty(self) -> bool:
        """Check if context is empty."""
        return not self.tissue and not self.cell_type and not self.ontology_ids


class Modality(str, Enum):
    """AlphaGenome prediction modalities."""
    RNA_EXPR = "RNA_EXPR"
    TSS_CAGE = "TSS_CAGE"
    ATAC_DNASE = "ATAC_DNASE"
    TF_BIND = "TF_BIND"
    HISTONE = "HISTONE"
    SPLICE_JUNCTION = "SPLICE_JUNCTION"
    SPLICE_SITE = "SPLICE_SITE"
    PAS = "PAS"
    CONTACT_MAP = "CONTACT_MAP"


class Direction(str, Enum):
    """Direction of regulatory effect."""
    UP = "up"
    DOWN = "down"
    MIXED = "mixed"
    NA = "n/a"


class EvidenceItem(BaseModel):
    """Single piece of regulatory evidence."""
    modality: Modality = Field(..., description="Data modality")
    description: str = Field(..., description="Human-readable description")
    delta: float = Field(..., description="Change magnitude (ALT - REF)")
    direction: Direction = Field(..., description="Direction of change")
    cell_specificity: Optional[float] = Field(None, ge=0, le=1, description="Cell-type specificity score")
    support_tracks: List[str] = Field(default_factory=list, description="Supporting track IDs")
    
    def format_description(self) -> str:
        """Format evidence with direction and magnitude."""
        direction_str = "↑" if self.direction == Direction.UP else "↓" if self.direction == Direction.DOWN else "↔"
        return f"{direction_str} {self.description} (Δ={self.delta:.3f})"


class PipelineRequest(BaseModel):
    """Request for pipeline execution."""
    variant: Optional[Variant] = Field(None, description="Variant to analyze")
    interval: Optional[GenomicInterval] = Field(None, description="Interval to analyze")
    context: Context = Field(default_factory=Context, description="Biological context")
    requested_modalities: Set[Modality] = Field(default_factory=set, description="Modalities to query")
    
    @field_validator("interval")
    def validate_input(cls, v: Optional[GenomicInterval], info) -> Optional[GenomicInterval]:
        """Ensure either variant or interval is provided."""
        if not v and hasattr(info, 'data') and not info.data.get("variant"):
            raise ValueError("Either variant or interval must be provided")
        return v


class PipelineResult(BaseModel):
    """Result from pipeline execution."""
    mechanism_summary: str = Field(..., description="1-3 sentence summary of mechanism")
    evidence: List[EvidenceItem] = Field(default_factory=list, description="Supporting evidence")
    figures: List[Path] = Field(default_factory=list, description="Generated figure paths")
    scores: Dict[str, float] = Field(default_factory=dict, description="Numerical scores")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    def get_primary_direction(self) -> Direction:
        """Get overall direction from evidence."""
        if not self.evidence:
            return Direction.NA
        
        up_count = sum(1 for e in self.evidence if e.direction == Direction.UP)
        down_count = sum(1 for e in self.evidence if e.direction == Direction.DOWN)
        
        if up_count > down_count:
            return Direction.UP
        elif down_count > up_count:
            return Direction.DOWN
        elif up_count > 0 and down_count > 0:
            return Direction.MIXED
        else:
            return Direction.NA
    
    def get_top_evidence(self, n: int = 3) -> List[EvidenceItem]:
        """Get top N evidence items by absolute delta."""
        return sorted(self.evidence, key=lambda e: abs(e.delta), reverse=True)[:n]