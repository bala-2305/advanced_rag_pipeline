"""Click CLI for mzero command line interface."""

import os
import click
from rich.console import Console
from rich.table import Table
from mzero.main import RAG

console = Console()


@click.group()
def cli():
    """mzero: Zero-Configuration RAG Framework CLI."""
    pass


@cli.command()
@click.option("--docs", default="./docs", help="Path to documentation directory.")
def init(docs):
    """Initialize mzero in current working directory."""
    os.makedirs(docs, exist_ok=True)
    rag = RAG(docs_path=docs)
    console.print(f"[bold green]✓ Initialized mzero with docs directory:[/] {docs}")


@cli.command()
@click.argument("path_or_url")
@click.option("--docs", default="./docs", help="Path to documentation directory.")
def add(path_or_url, docs):
    """Add a file, directory, or URL to the knowledge base."""
    rag = RAG(docs_path=docs)
    rag.add(path_or_url)
    console.print(f"[bold green]✓ Added and indexed:[/] {path_or_url}")


@cli.command()
@click.argument("question")
@click.option("--docs", default="./docs", help="Path to documentation directory.")
def ask(question, docs):
    """Ask a question against the knowledge base."""
    rag = RAG(docs_path=docs)
    res = rag.ask(question)
    
    console.print(f"\n[bold cyan]Question:[/] {question}")
    console.print(f"[bold green]Answer:[/] {res.answer}\n")
    
    if res.citations:
        table = Table(title="Citations & Grounding")
        table.add_column("Source File", style="cyan")
        table.add_column("Confidence", style="magenta")
        table.add_column("Snippet Preview", style="white")
        for cite in res.citations:
            table.add_row(cite.source_file, f"{cite.confidence}", cite.snippet[:60])
        console.print(table)


@cli.command()
@click.option("--docs", default="./docs", help="Path to documentation directory.")
@click.option("--port", default=8000, help="Port to serve dashboard and REST API.")
def serve(docs, port):
    """Serve REST API and Dashboard UI."""
    rag = RAG(docs_path=docs)
    rag.serve(port=port)


@cli.command()
@click.option("--docs", default="./docs", help="Path to documentation directory.")
def rebuild(docs):
    """Rebuild the index from scratch."""
    state_file = os.path.join(".mzero", "state.json")
    if os.path.exists(state_file):
        os.remove(state_file)
    rag = RAG(docs_path=docs)
    console.print("[bold green]✓ Index rebuilt successfully.[/]")


@cli.command()
@click.option("--docs", default="./docs", help="Path to documentation directory.")
def status(docs):
    """Show current knowledge base statistics."""
    rag = RAG(docs_path=docs)
    stats = rag.stats()
    
    table = Table(title="mzero System Status")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Total Documents", str(stats.total_documents))
    table.add_row("Total Chunks", str(stats.total_chunks))
    table.add_row("Total Queries", str(stats.total_queries))
    table.add_row("Cache Hit Rate", f"{stats.cache_hit_rate * 100:.1f}%")
    table.add_row("Embedding Model", stats.embedding_model)
    table.add_row("Vector DB Backend", stats.vector_db_backend)
    table.add_row("Uptime (s)", str(stats.uptime_seconds))
    
    console.print(table)


if __name__ == "__main__":
    cli()
