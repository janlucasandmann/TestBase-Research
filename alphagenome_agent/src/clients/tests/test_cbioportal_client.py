#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the CBioPortalClient against the live API."""

from typing import List, Dict, Any
import sys
from pathlib import Path

# Add the src directory to Python path for absolute imports
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.clients.cbioportal_client import CBioPortalClient

def test_client_fetch_kras_mutations() -> bool:
    print("== Test 1 (client): KRAS mutations from PAAD (TCGA PanCan 2018) ==")
    client = CBioPortalClient()
    # Explicit study id to be deterministic:
    study_id = "paad_tcga_pan_can_atlas_2018"

    muts: List[Dict[str, Any]] = client.get_mutations_in_gene("KRAS", study_id)
    print(f"   Got {len(muts)} KRAS mutations")
    print("\nFirst mutation: ", muts[0] if muts else "None")
    print("\n")

    for i, m in enumerate(muts[:3]):
        variant_info = (
            f"{m.get('chr','?')}:{m.get('startPosition','?')}:"
            f"{m.get('referenceAllele','?')}>{m.get('variantAllele','?')}"
        )
        print(f"   [{i+1}] {variant_info} ({m.get('proteinChange','?')})")

    # Look for G12V
    g12v = [m for m in muts if "G12V" in (m.get("proteinChange") or "")]
    if g12v:
        g = g12v[0]
        print(
            "   Found G12V at "
            f"chr{g.get('chr')}:{g.get('startPosition')}:"
            f"{g.get('referenceAllele')}>{g.get('variantAllele')} "
            f"sample={g.get('sampleId')}"
        )
    else:
        print("   G12V not found (still OK if other KRAS mutations returned)")

    return len(muts) > 0


def test_client_study_listing() -> bool:
    print("\n== Test 2 (client): List and filter studies ==")
    client = CBioPortalClient()

    studies = client.list_studies()
    print(f"   Got {len(studies)} studies")

    pancreatic = [
        s for s in studies
        if "pancreatic" in (s.get("name") or "").lower()
        or "paad" in (s.get("studyId") or "").lower()
    ]
    print(f"   Found {len(pancreatic)} pancreatic-related studies")
    for s in pancreatic[:3]:
        print(f"   - {s.get('studyId')}: {s.get('name')}")

    return len(pancreatic) > 0


if __name__ == "__main__":
    print("== cBioPortal Client Tests ==")
    print("=" * 60)

    ok1 = test_client_fetch_kras_mutations()
    ok2 = test_client_study_listing()

    print("\n== Results ==")
    print(f"   Client KRAS mutations: {'PASS' if ok1 else 'FAIL'}")
    print(f"   Client study listing : {'PASS' if ok2 else 'FAIL'}")

    if ok1 and ok2:
        print("\nSUCCESS")
        raise SystemExit(0)
    else:
        print("\nFAILURE")
        raise SystemExit(1)
