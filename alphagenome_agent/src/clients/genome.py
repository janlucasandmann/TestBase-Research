"""Biopython helpers for genome sequence operations."""

from typing import List, Optional, Tuple

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

from ..core.logging import get_logger
from ..core.schemas import GenomicInterval, Variant

logger = get_logger(__name__)


class GenomeClient:
    """Helper class for genomic sequence operations."""
    
    def __init__(self, fasta_path: Optional[str] = None):
        """Initialize with optional FASTA file.
        
        Args:
            fasta_path: Path to genome FASTA file
        """
        self.sequences = {}
        if fasta_path:
            self.load_fasta(fasta_path)
    
    def load_fasta(self, fasta_path: str) -> None:
        """Load genome sequences from FASTA file.
        
        Args:
            fasta_path: Path to FASTA file
        """
        try:
            for record in SeqIO.parse(fasta_path, "fasta"):
                chrom = record.id
                if not chrom.startswith("chr"):
                    chrom = f"chr{chrom}"
                self.sequences[chrom] = record.seq
                logger.info(f"Loaded {chrom}: {len(record.seq)} bp")
        except Exception as e:
            logger.error(f"Failed to load FASTA: {e}")
    
    def get_sequence(
        self,
        interval: GenomicInterval
    ) -> Optional[str]:
        """Get sequence for a genomic interval.
        
        Args:
            interval: Genomic interval
            
        Returns:
            DNA sequence string or None
        """
        if interval.chrom not in self.sequences:
            logger.warning(f"Chromosome {interval.chrom} not loaded")
            return None
        
        seq = self.sequences[interval.chrom]
        return str(seq[interval.start:interval.end])
    
    def get_variant_context(
        self,
        variant: Variant,
        window: int = 10
    ) -> Tuple[str, str, str]:
        """Get sequence context around a variant.
        
        Args:
            variant: Genomic variant
            window: Context window size
            
        Returns:
            Tuple of (left_context, variant_seq, right_context)
        """
        if variant.chrom not in self.sequences:
            return ("", variant.ref, "")
        
        seq = self.sequences[variant.chrom]
        left_start = max(0, variant.pos - window - 1)
        left_end = variant.pos - 1
        right_start = variant.pos + len(variant.ref) - 1
        right_end = min(len(seq), right_start + window)
        
        left_context = str(seq[left_start:left_end])
        right_context = str(seq[right_start:right_end])
        
        return (left_context, variant.ref, right_context)
    
    def create_windows(
        self,
        interval: GenomicInterval,
        window_size: int = 1000,
        step_size: Optional[int] = None
    ) -> List[GenomicInterval]:
        """Create sliding windows across an interval.
        
        Args:
            interval: Genomic interval
            window_size: Size of each window
            step_size: Step between windows (defaults to window_size)
            
        Returns:
            List of window intervals
        """
        if step_size is None:
            step_size = window_size
        
        windows = []
        pos = interval.start
        
        while pos < interval.end:
            window_end = min(pos + window_size, interval.end)
            windows.append(
                GenomicInterval(
                    chrom=interval.chrom,
                    start=pos,
                    end=window_end,
                    assembly=interval.assembly
                )
            )
            pos += step_size
        
        return windows
    
    def parse_variant_string(self, variant_str: str) -> Optional[Variant]:
        """Parse variant string format.
        
        Args:
            variant_str: Variant string (e.g., "chr1:123456:A>T")
            
        Returns:
            Variant object or None
        """
        try:
            parts = variant_str.split(":")
            if len(parts) != 3:
                raise ValueError("Invalid format")
            
            chrom = parts[0]
            pos = int(parts[1])
            alleles = parts[2].split(">")
            
            if len(alleles) != 2:
                raise ValueError("Invalid allele format")
            
            return Variant(
                chrom=chrom,
                pos=pos,
                ref=alleles[0],
                alt=alleles[1]
            )
        except Exception as e:
            logger.error(f"Failed to parse variant string '{variant_str}': {e}")
            return None
    
    def parse_interval_string(self, interval_str: str) -> Optional[GenomicInterval]:
        """Parse interval string format.
        
        Args:
            interval_str: Interval string (e.g., "chr1:100000-200000")
            
        Returns:
            GenomicInterval object or None
        """
        try:
            parts = interval_str.split(":")
            if len(parts) != 2:
                raise ValueError("Invalid format")
            
            chrom = parts[0]
            positions = parts[1].split("-")
            
            if len(positions) != 2:
                raise ValueError("Invalid position format")
            
            return GenomicInterval(
                chrom=chrom,
                start=int(positions[0]),
                end=int(positions[1])
            )
        except Exception as e:
            logger.error(f"Failed to parse interval string '{interval_str}': {e}")
            return None
    
    def find_nearest_genes(
        self,
        position: int,
        chrom: str,
        max_distance: int = 100000
    ) -> List[str]:
        """Find nearest genes to a position.
        
        Note: This is a stub - would require gene annotation data.
        
        Args:
            position: Genomic position
            chrom: Chromosome
            max_distance: Maximum search distance
            
        Returns:
            List of gene names
        """
        logger.info(f"Gene finding not implemented - would search near {chrom}:{position}")
        return []