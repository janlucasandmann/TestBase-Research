from __future__ import annotations

import base64
import datetime
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


# ---------- Small data models used by reporters ----------

@dataclass
class FigureSpec:
    caption: str
    path: Path


@dataclass
class VariantEntry:
    variant_id: str
    chrom: str
    pos: int
    ref: str
    alt: str
    status: str
    enhancers_detected: int = 0
    notes: Optional[str] = None
    figures: List[FigureSpec] = field(default_factory=list)
    modality_deltas: Dict[str, float] = field(default_factory=dict)


class ReportRenderer:
    """
    Generic, reusable HTML renderer for AlphaGenome reports.
    Produces a self-contained HTML file (images embedded as base64) with:
      - Executive summary
      - What we did (methods) in plain language
      - Per-mutation findings table
      - Visualizations for every mutation (any number of figures)
      - Limitations & interpretation

    This renderer is pipeline-agnostic and can be used by Enhancer, Splicing, PAS, etc.
    """

    def __init__(self, *, title: str = "AlphaGenome Report") -> None:
        self.title = title

    # ---------- HTML helpers ----------

    def _style(self) -> str:
        return (
            """
            <style>
              body { font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
                     margin: 24px; color: #1b1b1b; line-height: 1.45; }
              h1 { font-size: 26px; margin-bottom: 4px; }
              h2 { font-size: 20px; margin-top: 28px; }
              h3 { font-size: 16px; margin-top: 18px; }
              .meta { color: #555; font-size: 13px; margin-bottom: 16px; }
              .card { background: #fafafa; border: 1px solid #eee; border-radius: 10px; padding: 16px; margin: 14px 0; }
              .good { color: #0e7c2f; font-weight: 600; }
              .bad { color: #b00020; font-weight: 600; }
              .mut-table { width: 100%; border-collapse: collapse; font-size: 13px; }
              .mut-table th, .mut-table td { border: 1px solid #eee; padding: 8px; text-align: left; }
              .mut-table th { background: #f5f5f5; }
              .caption { color: #555; font-size: 12px; margin-top: 4px; }
              .disclaimer { color: #555; font-size: 12px; }
              .grid { display: grid; grid-template-columns: 1fr; gap: 10px; }
              .fig { border: 1px solid #eee; border-radius: 8px; padding: 10px; background: #fff; }
              .pill { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 12px; border: 1px solid #ddd; margin-right: 6px; }
            </style>
            """
        )

    def _header(self, meta: Dict[str, Any]) -> str:
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        rq = meta.get("research_question", "")
        return f"""
        <h1>{self.title}</h1>
        <div class=\"meta\">
          <div><b>Research question:</b> {rq}</div>
          <div><b>Gene:</b> {meta.get('gene','')} • <b>Cancer type:</b> {meta.get('cancer_type','')}</div>
          <div><b>Generated:</b> {date_str}</div>
          <div><b>Method:</b> Real AlphaGenome outputs (no mocking)</div>
        </div>
        """

    def _summary_card(self, summary: Dict[str, Any]) -> str:
        if summary.get("answer_yes", False):
            line = f"<div class=\"good\">✅ Answer: YES – {summary.get('yes_details','')}</div>"
        else:
            line = "<div class=\"bad\">❌ Answer: NO – No signal detected</div>"

        pills = []
        if "mutations_analyzed" in summary:
            pills.append(f"<span class=\"pill\">Mutations analyzed: {summary['mutations_analyzed']}</span>")
        if "enhancer_positive_variants" in summary:
            pills.append(f"<span class=\"pill\">Variants with enhancer signal: {summary['enhancer_positive_variants']}</span>")

        return f"""
        <div class=\"card\">
          <h2>Executive summary</h2>
          {line}
          <div style=\"margin-top:8px;\">{' '.join(pills)}</div>
        </div>
        """

    def _methods_card(self, meta: Dict[str, Any]) -> str:
        items = meta.get(
            "methods",
            [
                "Fetched mutations from cBioPortal.",
                "Scored each mutation with AlphaGenome for the relevant modalities.",
                "Reported exactly what AlphaGenome returned. No mock data.",
            ],
        )
        lis = "".join(f"<li>{x}</li>" for x in items)
        return f"""
        <div class=\"card\">
          <h2>What we did (methods, simplified)</h2>
          <ul>{lis}</ul>
          <div class=\"disclaimer\"><b>Note:</b> This report is for research use only and not for clinical decision-making.</div>
        </div>
        """

    def _mutations_table(self, variants: List[VariantEntry]) -> str:
        header = """
        <table class=\"mut-table\">
          <thead>
            <tr>
              <th>#</th><th>Variant</th><th>Status</th><th>Enhancers</th><th>Key modality deltas</th><th>Notes</th>
            </tr>
          </thead>
          <tbody>
        """
        rows = []
        for i, v in enumerate(variants, 1):
            label = f"{v.chrom}:{v.pos} {v.ref}>{v.alt}"
            deltas = ", ".join(f"{k}: {v.modality_deltas[k]:.2f}" for k in list(v.modality_deltas)[:4])
            rows.append(
                f"""
            <tr>
              <td>{i}</td>
              <td>{label}</td>
              <td>{v.status}</td>
              <td>{v.enhancers_detected}</td>
              <td>{deltas}</td>
              <td>{v.notes or ''}</td>
            </tr>"""
            )
        footer = "</tbody></table>"
        return f"<h2>Findings per mutation</h2>{header}{''.join(rows)}{footer}"

    def _embed_image_html(self, path: Path, alt: str, width: int = 760) -> str:
        b64 = base64.b64encode(path.read_bytes()).decode("utf-8")
        return f'<img alt="{alt}" src="data:image/png;base64,{b64}" width="{width}"/>'

    def _visuals_section(self, variants: List[VariantEntry]) -> str:
        blocks = []
        for v in variants:
            figs_html = "".join(
                f'<div class="fig">{self._embed_image_html(f.path, f.caption)}'
                f'<div class="caption">{f.caption}</div></div>'
                for f in v.figures
            )
            blocks.append(
                f"""
            <div class=\"card\">
              <h3>Variant: {v.chrom}:{v.pos} {v.ref}&gt;{v.alt}</h3>
              <div class=\"grid\">{figs_html}</div>
            </div>"""
            )
        return "<h2>Visualizations</h2>" + "".join(blocks)

    def _limitations_card(self, meta: Dict[str, Any]) -> str:
        items = meta.get(
            "limitations",
            [
                "AlphaGenome predictions are in-silico estimates and require experimental validation.",
                "Effects can be cell-type specific; we approximate with the closest available tissue context.",
                "Very large structural variants may be out of scope for the analyzed window.",
            ],
        )
        lis = "".join(f"<li>{x}</li>" for x in items)
        return f"""
        <div class=\"card\">
          <h2>Limitations & interpretation</h2>
          <ul>{lis}</ul>
        </div>
        """

    def build_html(self, *, meta: Dict[str, Any], variants: List[VariantEntry], summary: Dict[str, Any]) -> str:
        parts = [
            "<html><head><meta charset='utf-8'>",
            self._style(),
            "</head><body>",
            self._header(meta),
            self._summary_card(summary),
            self._methods_card(meta),
            self._mutations_table(variants),
            self._visuals_section(variants),
            self._limitations_card(meta),
            "</body></html>",
        ]
        return "".join(parts)

    def save(self, html: str, out_path: Path) -> Path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html, encoding="utf-8")
        return out_path



