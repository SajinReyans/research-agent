import os
import sys
import argparse
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from agent.parser import extract_text_from_pdf, chunk_text
from agent.summarizer import summarize_long_paper
from agent.searcher import search_papers, display_papers, pick_paper
from agent.downloader import download_pdf

console = Console()


def save_summary(summary: str, title: str) -> str:
    """
    Saves the summary to the outputs folder as a markdown file.

    Args:
        summary: The generated summary text.
        title: Title used to name the output file.

    Returns:
        Path to saved summary file.
    """
    os.makedirs("outputs", exist_ok=True)

    # Clean title for use as filename
    clean_title = "".join(c if c.isalnum() or c in " _-" else "" for c in title)
    clean_title = clean_title.strip().replace(" ", "_")[:50]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"outputs/{clean_title}_summary_{timestamp}.md"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# Summary: {title}\n")
        f.write(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        f.write("---\n\n")
        f.write(summary)

    return output_path


def run_pdf_mode(pdf_path: str):
    """
    Phase 1 mode: Directly summarize a local PDF file.

    Args:
        pdf_path: Path to the PDF file.
    """
    if not os.path.exists(pdf_path):
        console.print(f"[bold red]❌ File not found:[/bold red] {pdf_path}")
        sys.exit(1)

    if not pdf_path.lower().endswith(".pdf"):
        console.print("[bold red]❌ Please provide a valid .pdf file.[/bold red]")
        sys.exit(1)

    console.print("\n[bold]Step 1/3 → Extracting text from PDF...[/bold]")
    text = extract_text_from_pdf(pdf_path)

    console.print("\n[bold]Step 2/3 → Preparing text for LLM...[/bold]")
    chunks = chunk_text(text, max_chars=12000)

    console.print("\n[bold]Step 3/3 → Generating summary with Groq...[/bold]")
    summary = summarize_long_paper(chunks)

    console.print("\n")
    console.print(Panel(Markdown(summary), title="📄 Paper Summary", border_style="green"))

    title = os.path.splitext(os.path.basename(pdf_path))[0]
    output_path = save_summary(summary, title)
    console.print(f"\n[bold green]💾 Summary saved to:[/bold green] {output_path}")


def run_search_mode(query: str):
    """
    Phase 2 mode: Search ArXiv, pick a paper, download and summarize it.

    Args:
        query: Search keyword or topic.
    """
    # Step 1: Search ArXiv
    console.print("\n[bold]Step 1/4 → Searching ArXiv...[/bold]")
    papers = search_papers(query, max_results=5)

    if not papers:
        sys.exit(1)

    # Step 2: Display results and let user pick
    console.print("\n[bold]Step 2/4 → Select a paper...[/bold]")
    display_papers(papers)
    selected_paper = pick_paper(papers)

    # Step 3: Download the PDF
    console.print("\n[bold]Step 3/4 → Downloading PDF...[/bold]")
    pdf_path = download_pdf(selected_paper)

    # Step 4: Summarize
    console.print("\n[bold]Step 4/4 → Summarizing paper...[/bold]")
    text = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(text, max_chars=12000)
    summary = summarize_long_paper(chunks)

    console.print("\n")
    console.print(Panel(Markdown(summary), title="📄 Paper Summary", border_style="green"))

    output_path = save_summary(summary, selected_paper["title"])
    console.print(f"\n[bold green]💾 Summary saved to:[/bold green] {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Research Agent: Summarize research papers using Groq LLM",
        formatter_class=argparse.RawTextHelpFormatter
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "pdf",
        type=str,
        nargs="?",
        help="Path to a local PDF file to summarize"
    )
    group.add_argument(
        "--search",
        type=str,
        metavar="QUERY",
        help="Search ArXiv for papers by keyword/topic"
    )

    args = parser.parse_args()

    console.print(Panel.fit(
        "[bold magenta]🔬 Research Agent[/bold magenta]\n"
        "[dim]Powered by Groq + LLaMA 3 + ArXiv[/dim]",
        border_style="magenta"
    ))

    if args.search:
        run_search_mode(args.search)
    elif args.pdf:
        run_pdf_mode(args.pdf)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()