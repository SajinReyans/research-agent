import os
import urllib.request
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

DOWNLOAD_DIR = "downloads"


def download_pdf(paper: dict) -> str:
    """
    Downloads a research paper PDF from ArXiv.

    Args:
        paper: Paper metadata dict containing pdf_url, arxiv_id, title.

    Returns:
        Local file path of the downloaded PDF.
    """
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    # Create a clean filename from arxiv_id
    filename = f"{paper['arxiv_id'].replace('/', '_')}.pdf"
    filepath = os.path.join(DOWNLOAD_DIR, filename)

    # Skip download if already exists
    if os.path.exists(filepath):
        console.print(f"[bold yellow]⚡ PDF already downloaded:[/bold yellow] {filepath}")
        return filepath

    console.print(f"\n[bold cyan]⬇️  Downloading PDF...[/bold cyan]")
    console.print(f"[dim]URL: {paper['pdf_url']}[/dim]")

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Downloading...", total=None)
            urllib.request.urlretrieve(paper["pdf_url"], filepath)

        size_kb = os.path.getsize(filepath) // 1024
        console.print(f"[bold green]✅ Downloaded:[/bold green] {filepath} ({size_kb} KB)")
        return filepath

    except Exception as e:
        console.print(f"[bold red]❌ Download failed:[/bold red] {e}")
        raise