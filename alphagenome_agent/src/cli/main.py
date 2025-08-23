"""Command line interface for TestBase Research AlphaGenome pipeline."""

import sys
from pathlib import Path
from typing import Optional, Set

import typer
from rich.console import Console
from rich.table import Table

from ..core.config import config
from ..core.logging import get_logger
from ..core.schemas import (
    Assembly, Context, GenomicInterval, Modality, PipelineRequest, Variant
)
from ..pipelines.promoter_enhancer import PromoterEnhancerPipeline

logger = get_logger(__name__)
console = Console()
app = typer.Typer(help="TestBase Research AlphaGenome Pipeline")


@app.command()
def run(
    pipeline: str = typer.Argument(..., help="Pipeline to run (promoter-enhancer)"),
    variant: Optional[str] = typer.Option(None, "--variant", help="Variant in format chr:pos:ref>alt"),
    interval: Optional[str] = typer.Option(None, "--interval", help="Interval in format chr:start-end"),
    assembly: Assembly = typer.Option(Assembly.HG38, "--assembly", help="Genome assembly"),
    tissue: Optional[str] = typer.Option(None, "--tissue", help="Tissue context"),
    cell_type: Optional[str] = typer.Option(None, "--cell-type", help="Cell type context"),
    outdir: Path = typer.Option(Path("data/outputs"), "--outdir", help="Output directory"),
    use_mock: bool = typer.Option(False, "--use-mock", help="Use mock data instead of API"),
    pdf: bool = typer.Option(True, "--pdf/--no-pdf", help="Generate PDF report"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """Run AlphaGenome analysis pipeline."""
    
    # Set up logging
    if verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Set mock mode if requested
    if use_mock:
        import os
        os.environ["USE_MOCK"] = "1"
        console.print("[yellow]Using mock data mode[/yellow]")
    
    # Parse variant or interval
    parsed_variant = None
    parsed_interval = None
    
    if variant:
        try:
            parsed_variant = parse_variant(variant, assembly)
            console.print(f"[green]Analyzing variant:[/green] {parsed_variant.to_string()}")
        except ValueError as e:
            console.print(f"[red]Error parsing variant:[/red] {e}")
            sys.exit(1)
    elif interval:
        try:
            parsed_interval = parse_interval(interval, assembly)
            console.print(f"[green]Analyzing interval:[/green] {parsed_interval.to_string()}")
        except ValueError as e:
            console.print(f"[red]Error parsing interval:[/red] {e}")
            sys.exit(1)
    else:
        console.print("[red]Error:[/red] Either --variant or --interval must be provided")
        sys.exit(1)
    
    # Create context
    context = Context(tissue=tissue, cell_type=cell_type)
    
    # Create request
    request = PipelineRequest(
        variant=parsed_variant,
        interval=parsed_interval,
        context=context,
        requested_modalities=set()  # Pipeline will determine modalities
    )
    
    # Run pipeline
    try:
        console.print(f"[blue]Running {pipeline} pipeline...[/blue]")
        
        if pipeline == "promoter-enhancer":
            import os
            pipeline_instance = PromoterEnhancerPipeline(api_key=os.getenv("ALPHAGENOME_API_KEY"))
            result = pipeline_instance.run(request)
        else:
            console.print(f"[red]Error:[/red] Unknown pipeline: {pipeline}")
            sys.exit(1)
        
        # Display results
        display_results(result)
        
        # Save outputs to specified directory
        if outdir != Path("data/outputs"):
            save_outputs_to_directory(result, outdir)
        
        console.print(f"[green]Pipeline completed successfully![/green]")
        console.print(f"[blue]Report saved to:[/blue] {result.metadata.get('report_path', 'N/A')}")
        
    except Exception as e:
        console.print(f"[red]Pipeline failed:[/red] {e}")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)


@app.command()
def list_modalities():
    """List available AlphaGenome modalities."""
    console.print("[blue]Available AlphaGenome modalities:[/blue]")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Modality", style="cyan")
    table.add_column("Description", style="white")
    
    modality_descriptions = {
        "RNA_EXPR": "RNA expression levels",
        "TSS_CAGE": "Transcription start site activity (CAGE)",
        "ATAC_DNASE": "Chromatin accessibility (ATAC-seq, DNase-seq)",
        "TF_BIND": "Transcription factor binding",
        "HISTONE": "Histone modifications",
        "SPLICE_JUNCTION": "Splice junction usage",
        "SPLICE_SITE": "Splice site strength",
        "PAS": "Polyadenylation site usage",
        "CONTACT_MAP": "3D chromatin contact maps"
    }
    
    for modality in Modality:
        description = modality_descriptions.get(modality.value, "")
        table.add_row(modality.value, description)
    
    console.print(table)


@app.command()
def version():
    """Show version information."""
    console.print("[blue]TestBase Research AlphaGenome Pipeline[/blue]")
    console.print("Version: 0.1.0")
    console.print("API: AlphaGenome")


def parse_variant(variant_str: str, assembly: Assembly) -> Variant:
    """Parse variant string into Variant object.
    
    Args:
        variant_str: Variant string in format chr:pos:ref>alt
        assembly: Genome assembly
        
    Returns:
        Parsed Variant object
    """
    try:
        if ":" not in variant_str or ">" not in variant_str:
            raise ValueError("Variant must be in format chr:pos:ref>alt")
        
        parts = variant_str.split(":")
        if len(parts) != 3:
            raise ValueError("Variant must be in format chr:pos:ref>alt")
        
        chrom = parts[0]
        pos = int(parts[1])
        ref_alt = parts[2].split(">")
        
        if len(ref_alt) != 2:
            raise ValueError("Variant must be in format chr:pos:ref>alt")
        
        ref, alt = ref_alt
        
        return Variant(
            chrom=chrom,
            pos=pos,
            ref=ref,
            alt=alt,
            assembly=assembly
        )
        
    except (ValueError, IndexError) as e:
        raise ValueError(f"Invalid variant format '{variant_str}': {e}")


def parse_interval(interval_str: str, assembly: Assembly) -> GenomicInterval:
    """Parse interval string into GenomicInterval object.
    
    Args:
        interval_str: Interval string in format chr:start-end
        assembly: Genome assembly
        
    Returns:
        Parsed GenomicInterval object
    """
    try:
        if ":" not in interval_str or "-" not in interval_str:
            raise ValueError("Interval must be in format chr:start-end")
        
        parts = interval_str.split(":")
        if len(parts) != 2:
            raise ValueError("Interval must be in format chr:start-end")
        
        chrom = parts[0]
        start_end = parts[1].split("-")
        
        if len(start_end) != 2:
            raise ValueError("Interval must be in format chr:start-end")
        
        start = int(start_end[0])
        end = int(start_end[1])
        
        return GenomicInterval(
            chrom=chrom,
            start=start,
            end=end,
            assembly=assembly
        )
        
    except (ValueError, IndexError) as e:
        raise ValueError(f"Invalid interval format '{interval_str}': {e}")


def display_results(result):
    """Display pipeline results in a formatted table.
    
    Args:
        result: PipelineResult object
    """
    console.print("\n[bold blue]Analysis Results:[/bold blue]")
    
    # Mechanism summary
    console.print(f"[bold]Mechanism Summary:[/bold] {result.mechanism_summary}")
    
    # Evidence table
    if result.evidence:
        console.print("\n[bold]Evidence:[/bold]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Modality", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("Delta", style="yellow")
        table.add_column("Direction", style="green")
        
        for evidence in result.evidence:
            direction_symbol = "↑" if evidence.direction.value == "up" else "↓" if evidence.direction.value == "down" else "↔"
            table.add_row(
                evidence.modality.value,
                evidence.description,
                f"{evidence.delta:.4f}",
                f"{direction_symbol} {evidence.direction.value}"
            )
        
        console.print(table)
    
    # Scores
    if result.scores:
        console.print("\n[bold]Scores:[/bold]")
        
        score_table = Table(show_header=True, header_style="bold magenta")
        score_table.add_column("Metric", style="cyan")
        score_table.add_column("Value", style="yellow")
        
        for metric, value in result.scores.items():
            if isinstance(value, float):
                score_table.add_row(metric, f"{value:.4f}")
            else:
                score_table.add_row(metric, str(value))
        
        console.print(score_table)
    
    # Figures
    if result.figures:
        console.print(f"\n[bold]Generated {len(result.figures)} figures:[/bold]")
        for fig_path in result.figures:
            console.print(f"  • {fig_path}")


def save_outputs_to_directory(result, outdir: Path):
    """Save pipeline outputs to specified directory.
    
    Args:
        result: PipelineResult object
        outdir: Output directory path
    """
    try:
        outdir.mkdir(parents=True, exist_ok=True)
        
        # Copy figures
        if result.figures:
            figures_dir = outdir / "figures"
            figures_dir.mkdir(exist_ok=True)
            
            for fig_path in result.figures:
                if fig_path.exists():
                    import shutil
                    shutil.copy2(fig_path, figures_dir / fig_path.name)
        
        # Copy report if available
        report_path = result.metadata.get('report_path')
        if report_path and Path(report_path).exists():
            import shutil
            shutil.copy2(report_path, outdir / "report.html")
        
        console.print(f"[green]Outputs saved to:[/green] {outdir}")
        
    except Exception as e:
        console.print(f"[yellow]Warning: Failed to save outputs to {outdir}: {e}[/yellow]")


if __name__ == "__main__":
    app()