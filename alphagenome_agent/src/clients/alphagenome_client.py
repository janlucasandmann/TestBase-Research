"""AlphaGenome client — thin, reusable wrapper around the official API.

Dependencies:
  pip install alphagenome
Docs:
  - Quick start & API surface: alphagenome docs/colabs
"""

from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Literal, Optional

from alphagenome.models import dna_client
from alphagenome.data import genome

# -------- Logging -------------------------------------------------------------

logger = logging.getLogger("alphagenome_client")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

# -------- Public datatypes (small façade over alphagenome) --------------------

TissueName = Literal["breast", "pancreatic", "colorectal", "lung"]
# Expand later if you like; keep mapping centralized in the client.


@dataclass(frozen=True)
class VariantSpec:
    """Minimal variant spec so callers don't depend on alphagenome internals."""
    chrom: str
    pos: int
    ref: str
    alt: str

# -------- Client --------------------------------------------------------------

class AlphaGenomeClient:
    """Tiny wrapper that standardizes model creation & common predictions."""

    # Minimal, explicit tissue mapping (UBERON IDs per docs/examples)
    _TISSUE_UBERON = {
        "breast": "UBERON:0000310",
        "pancreatic": "UBERON:0001264",
        "colorectal": "UBERON:0001157",
        "lung": "UBERON:0002048",
    }

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("ALPHAGENOME_API_KEY is required")
        self.api_key = api_key
        self._model = dna_client.create(api_key)  # official entrypoint
        logger.info("AlphaGenome model ready")

    # ---- Helpers -------------------------------------------------------------

    @classmethod
    def tissue_to_terms(cls, tissue: TissueName | str | None) -> List[str]:
        if not tissue:
            return []
        key = str(tissue).lower()
        return [cls._TISSUE_UBERON.get(key, key)]

    @staticmethod
    def _variant_to_alphagenome(v: VariantSpec) -> genome.Variant:
        # alphagenome Variant signature per docs
        return genome.Variant(
            chromosome=v.chrom,
            position=v.pos,
            reference_bases=v.ref,
            alternate_bases=v.alt,
        )

    # ---- Public API ----------------------------------------------------------

    def predict_variant_effects(
        self,
        variant: VariantSpec,
        interval_bp: int = 131_072,
        requested_outputs: Optional[Iterable[dna_client.OutputType]] = None,
        tissue: Optional[TissueName | str] = None,
    ) -> Dict[str, Any]:
        """One-stop variant effect prediction (REF vs ALT) in a fixed window.

        Returns a dict with raw alphagenome outputs plus a small numeric summary.
        """
        if requested_outputs is None:
            requested_outputs = (
                dna_client.OutputType.DNASE,
                dna_client.OutputType.CHIP_HISTONE,
                dna_client.OutputType.RNA_SEQ,
            )

        ag_variant = self._variant_to_alphagenome(variant)
        interval = ag_variant.reference_interval.resize(interval_bp)

        outputs = self._model.predict_variant(
            interval=interval,
            variant=ag_variant,
            requested_outputs=list(requested_outputs),
            ontology_terms=self.tissue_to_terms(tissue),
        )

        # Small numeric summary (means & max deltas where available)
        summary: Dict[str, Any] = {}

        def safe_stats(ref_tensor, alt_tensor):
            import numpy as np
            r = ref_tensor.values
            a = alt_tensor.values
            return {
                "ref_mean": float(r.mean()) if r.size else 0.0,
                "alt_mean": float(a.mean()) if a.size else 0.0,
                "max_increase": float((a - r).max()) if r.size and a.size else 0.0,
            }

        if getattr(outputs.reference, "dnase", None) is not None:
            summary["dnase"] = safe_stats(outputs.reference.dnase, outputs.alternate.dnase)

        if getattr(outputs.reference, "rna_seq", None) is not None:
            summary["rna_seq"] = safe_stats(outputs.reference.rna_seq, outputs.alternate.rna_seq)

        if getattr(outputs.reference, "chip_histone", None) is not None:
            ref = outputs.reference.chip_histone
            alt = outputs.alternate.chip_histone
            meta = ref.metadata if hasattr(ref, 'metadata') and ref.metadata is not None else {}
            mark_names = list(meta.get("name", [])) if isinstance(meta, dict) else []
            # Per-mark means/max-increase
            import numpy as np
            marks = {}
            if ref.values.size and alt.values.size:
                for i, name in enumerate(mark_names[: ref.values.shape[1]]):
                    r = ref.values[:, i]
                    a = alt.values[:, i]
                    marks[str(name)] = {
                        "ref_mean": float(np.mean(r)),
                        "alt_mean": float(np.mean(a)),
                        "max_increase": float(np.max(a - r)),
                    }
            summary["chip_histone"] = {"marks": marks, "mark_names": mark_names}

        return {
            "variant": f"{variant.chrom}:{variant.pos}:{variant.ref}>{variant.alt}",
            "interval_bp": interval_bp,
            "tissue_terms": self.tissue_to_terms(tissue),
            "summary": summary,
            # Expose raw for downstream plots/pipelines if needed:
            "raw": {
                "reference": outputs.reference,
                "alternate": outputs.alternate,
            },
        }

    def predict_sequence(
        self,
        sequence: str,
        requested_outputs: Optional[Iterable[dna_client.OutputType]] = None,
        tissue: Optional[TissueName | str] = None,
    ) -> Dict[str, Any]:
        """Direct sequence inference (useful for multi-variant/edited sequences)."""
        if requested_outputs is None:
            requested_outputs = (dna_client.OutputType.RNA_SEQ,)
        outputs = self._model.predict_sequence(
            sequence=sequence,
            requested_outputs=list(requested_outputs),
            ontology_terms=self.tissue_to_terms(tissue),
        )
        return {
            "tissue_terms": self.tissue_to_terms(tissue),
            "raw": outputs,
        }
