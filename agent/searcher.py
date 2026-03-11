import arxiv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()


def search_papers(query: str, max_results: int = 5) -> list[dict]:
    """
    Searches ArXiv for papers matching the query.

    Args:
        query: Search keyword or topic.
        max_results: Number of papers to return.

    Returns:
        List of paper metadata dicts.
    """
    console.print(f"\n[bold cyan]🔍 Searching ArXiv for:[/bold cyan] [yellow]{query}[/yellow]")

    try:
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )

        results = list(client.results(search))

        if not results:
            console.print("[bold red]❌ No papers found. Try a different keyword.[/bold red]")
            return []

        papers = []
        for i, result in enumerate(results, start=1):
            papers.append({
                "index": i,
                "title": result.title,
                "authors": ", ".join(a.name for a in result.authors[:3]) + (
                    " et al." if len(result.authors) > 3 else ""
                ),
                "published": result.published.strftime("%Y-%m-%d"),
                "abstract": result.summary[:300] + "..." if len(result.summary) > 300 else result.summary,
                "pdf_url": result.pdf_url,
                "arxiv_id": result.entry_id.split("/")[-1]
            })

        console.print(f"[bold green]✅ Found {len(papers)} papers.[/bold green]\n")
        return papers

    except Exception as e:
        console.print(f"[bold red]❌ ArXiv search error:[/bold red] {e}")
        raise


def display_papers(papers: list[dict]):
    """
    Displays papers in a nicely formatted table.

    Args:
        papers: List of paper metadata dicts.
    """
    table = Table(
        title="📚 ArXiv Search Results",
        box=box.ROUNDED,
        show_lines=True,
        header_style="bold magenta"
    )

    table.add_column("#", style="bold cyan", width=3, justify="center")
    table.add_column("Title", style="bold white", min_width=35)
    table.add_column("Authors", style="dim white", min_width=20)
    table.add_column("Date", style="green", width=12, justify="center")

    for paper in papers:
        table.add_row(
            str(paper["index"]),
            paper["title"],
            paper["authors"],
            paper["published"]
        )

    console.print(table)

    # Show abstracts below the table
    for paper in papers:
        console.print(Panel(
            f"[dim]{paper['abstract']}[/dim]",
            title=f"[bold cyan][{paper['index']}] Abstract[/bold cyan]",
            border_style="dim",
            expand=False
        ))


def pick_paper(papers: list[dict]) -> dict:
    """
    Prompts the user to pick a paper from the list.

    Args:
        papers: List of paper metadata dicts.

    Returns:
        Selected paper metadata dict.
    """
    while True:
        try:
            choice = input(f"\n👉 Pick a paper to summarize (1-{len(papers)}), or 0 to exit: ").strip()

            if choice == "0":
                console.print("[dim]Exiting...[/dim]")
                exit(0)

            choice = int(choice)
            if 1 <= choice <= len(papers):
                selected = papers[choice - 1]
                console.print(f"\n[bold green]✅ Selected:[/bold green] {selected['title']}")
                return selected
            else:
                console.print(f"[yellow]⚠️  Please enter a number between 1 and {len(papers)}.[/yellow]")

        except ValueError:
            console.print("[yellow]⚠️  Invalid input. Please enter a number.[/yellow]")