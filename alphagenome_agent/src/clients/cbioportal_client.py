#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cBioPortal API client."""

from typing import Any, Dict, List, Optional, Tuple
import requests

class CBioPortalClient:
    """
    Thin client for cBioPortal's public REST API.
    Focus: fetching mutation data for a gene within a study.
    """

    def __init__(self, api_url: str = "https://www.cbioportal.org/api", timeout: int = 30):
        """
        Args:
            api_url: Base URL for cBioPortal API.
            timeout: Default request timeout in seconds.
        """
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
        })

    def list_molecular_profiles(self, study_id: str) -> List[Dict[str, Any]]:
        url = f"{self.api_url}/molecular-profiles"
        r = self._session.get(url, params={"studyId": study_id}, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def ensure_mutation_profile(self, study_id: str) -> str:
        """Pick a mutation profile for the study, preferring MUTATION_EXTENDED or {study}_mutations."""
        profiles = self.list_molecular_profiles(study_id)
        ids = {p["molecularProfileId"]: p for p in profiles}

        # Prefer a profile whose geneticAlterationType starts with MUTATION (esp. EXTENDED)
        best = None
        for p in profiles:
            gat = (p.get("geneticAlterationType") or "").upper()
            if gat.startswith("MUTATION_EXTENDED"):
                return p["molecularProfileId"]
            if gat.startswith("MUTATION"):
                best = best or p["molecularProfileId"]

        # Conventional fallback
        cand = f"{study_id}_mutations"
        if cand in ids:
            return cand

        if best:
            return best
        raise RuntimeError(f"No mutation profile found for study '{study_id}'. Profiles={list(ids.keys())}")

    def list_sample_lists(self, study_id: str) -> List[Dict[str, Any]]:
        url = f"{self.api_url}/sample-lists"
        r = self._session.get(url, params={"studyId": study_id}, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def pick_sample_list_id(self, study_id: str, preferred_suffix: str = "sequenced") -> Optional[str]:
        """Prefer a 'sequenced' list; otherwise fall back to something usable (e.g., *_all)."""
        lists = self.list_sample_lists(study_id)
        ids = [sl["sampleListId"] for sl in lists]

        exact_prefs = [f"{study_id}_{preferred_suffix}", f"{study_id}_sequenced", f"{study_id}_all"]
        for x in exact_prefs:
            if x in ids:
                return x

        # fuzzy fallback
        for s in ids:
            if "sequenced" in s:
                return s
        for s in ids:
            if s.endswith("_all") or "all" in s:
                return s

        return ids[0] if ids else None

    def get_sample_ids_for_list(self, sample_list_id: str) -> List[str]:
        url = f"{self.api_url}/sample-lists/{sample_list_id}/sample-ids"
        r = self._session.get(url, timeout=self.timeout)
        r.raise_for_status()
        return r.json() or []

    # ---------- Public API ----------
    def list_studies(self) -> List[Dict[str, Any]]:
        url = f"{self.api_url}/studies"
        r = self._session.get(url, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def find_study(self, cancer_type_or_study_id: Optional[str]) -> Tuple[str, str]:
        default_study = "paad_tcga_pan_can_atlas_2018"

        if not cancer_type_or_study_id:
            study_id = default_study
        else:
            wanted = cancer_type_or_study_id.lower()
            studies = self.list_studies()

            exact = [s for s in studies if s.get("studyId", "").lower() == wanted]
            if exact:
                study_id = exact[0]["studyId"]
            else:
                candidates = [
                    s for s in studies
                    if wanted in (s.get("studyId") or "").lower()
                    or wanted in (s.get("name") or "").lower()
                ]
                study_id = candidates[0]["studyId"] if candidates else default_study

        # The second element is ignored now; we re-resolve mutation profile dynamically.
        return study_id, f"{study_id}_mutations"

    def get_mutations_in_gene(
        self,
        gene_symbol: str,
        cancer_type_or_study_id: Optional[str] = None,
        sample_list_suffix: str = "sequenced",  # prefer sequenced by default
    ) -> List[Dict[str, Any]]:
        study_id, _ = self.find_study(cancer_type_or_study_id)
        molecular_profile_id = self.ensure_mutation_profile(study_id)

        sample_list_id = self.pick_sample_list_id(study_id, preferred_suffix=sample_list_suffix)
        if not sample_list_id:
            raise RuntimeError(f"No sample lists found for study '{study_id}'.")

        # ---- Attempt 1: GET that supports sampleListId in the query
        get_url = f"{self.api_url}/molecular-profiles/{molecular_profile_id}/mutations"
        params = {
            "sampleListId": sample_list_id,
            "hugoGeneSymbol": gene_symbol,   # note: singular in GET
            "projection": "DETAILED",
            "pageNumber": 0,
            "pageSize": 10000,
        }
        r = self._session.get(get_url, params=params, timeout=self.timeout)
        if r.status_code == 200:
            data = r.json()
            return data if isinstance(data, list) else []

        # ---- Attempt 2: POST /mutations/fetch with resolved sampleIds
        sample_ids = self.get_sample_ids_for_list(sample_list_id)
        if not sample_ids:
            return []

        post_url = f"{self.api_url}/molecular-profiles/{molecular_profile_id}/mutations/fetch"
        payload = {
            "hugoGeneSymbols": [gene_symbol],  # plural in POST
            "sampleIds": sample_ids,
            "projection": "DETAILED",
        }
        r = self._session.post(post_url, json=payload, timeout=self.timeout)
        try:
            r.raise_for_status()
        except requests.HTTPError as e:
            # expose server message so the next failure is actionable
            raise requests.HTTPError(
                f"{e}\n"
                f"Study: {study_id}\n"
                f"Molecular profile: {molecular_profile_id}\n"
                f"Sample list: {sample_list_id}\n"
                f"N(sampleIds)={len(sample_ids)}\n"
                f"Server said: {r.text}"
            ) from e

        data = r.json()
        return data if isinstance(data, list) else []

    def get_mutation_frequency(
        self,
        gene_symbol: str,
        aa_change_substring: str,
        cancer_type_or_study_id: Optional[str] = None,
    ) -> float:
        muts = self.get_mutations_in_gene(gene_symbol, cancer_type_or_study_id)
        if not muts:
            return 0.0

        samples = {m.get("sampleId") for m in muts if m.get("sampleId")}
        if not samples:
            return 0.0

        hits = [
            m for m in muts
            if aa_change_substring.upper() in (m.get("proteinChange") or "").upper()
        ]
        hit_samples = {m.get("sampleId") for m in hits if m.get("sampleId")}
        return len(hit_samples) / len(samples)