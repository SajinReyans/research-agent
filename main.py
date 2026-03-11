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
from agent.reader import extract_from_chunks, display_extraction
from agent.comparator import compare_papers, display_comparison

console = Console()


def save_full_report(summary: str, extraction: str, title: str) -> str:
    """
    Saves the combined summary + extraction report to outputs folder.

    Args:
        summary: Generated summary text.
        extraction: Extracted methodology details.
        title: Title used to name the output file.

    Returns:
        Path to saved report file.
    """
    os.makedirs("outputs", exist_ok=True)

    clean_title = "".join(c if c.isalnum() or c in " _-" else "" for c in title)
    clean_title = clean_title.strip().replace(" ", "_")[:50]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"outputs/{clean_title}_full_report_{timestamp}.md"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# Full Report: {title}\n")
        f.write(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        f.write("---\n\n")
        f.write("# 📄 Part 1: Summary\n\n")
        f.write(summary)
        f.write("\n\n---\n\n")
        f.write("# 🔬 Part 2: Methodology Extraction\n\n")
        f.write(extraction)

    return output_path


def save_comparison_report(comparison: str, title1: str, title2: str) -> str:
    """
    Saves the comparison report to the outputs folder.

    Args:
        comparison: Full comparison report string.
        title1: Title of Paper 1.
        title2: Title of Paper 2.

    Returns:
        Path to saved comparison report.
    """
    os.makedirs("outputs", exist_ok=True)

    clean1 = "".join(c if c.isalnum() or c in " _-" else "" for c in title1).strip().replace(" ", "_")[:25]
    clean2 = "".join(c if c.isalnum() or c in " _-" else "" for c in title2).strip().replace(" ", "_")[:25]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"outputs/comparison_{clean1}_vs_{clean2}_{timestamp}.md"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# Comparison Report\n")
        f.write(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        f.write(f"**Paper 1:** {title1}\n\n")
        f.write(f"**Paper 2:** {title2}\n\n")
        f.write("---\n\n")
        f.write(comparison)

    return output_path


def process_single_paper(paper: dict, label: str) -> tuple[str, str, list[str]]:
    """
    Downloads, extracts text, summarizes and extracts methodology from a paper.

    Args:
        paper: Paper metadata dict.
        label: Label for display (e.g. "Paper 1").

    Returns:
        Tuple of (summary, extraction, chunks).
    """
    console.print(f"\n[bold magenta]── Processing {label}: {paper['title'][:60]}... ──[/bold magenta]")

    # Download
    console.print(f"\n[bold]→ Downloading PDF...[/bold]")
    pdf_path = download_pdf(paper)

    # Parse
    console.print(f"\n[bold]→ Extracting text...[/bold]")
    text = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(text, max_chars=12000)

    # Summarize
    console.print(f"\n[bold]→ Summarizing...[/bold]")
    summary = summarize_long_paper(chunks)
    console.print(Panel(Markdown(summary), title=f"📄 {label} Summary", border_style="green"))

    # Extract
    console.print(f"\n[bold]→ Extracting methodology...[/bold]")
    extraction = extract_from_chunks(chunks)
    display_extraction(extraction)

    return summary, extraction, chunks


def run_compare_mode(query: str):
    """
    Phase 4 mode: Search, pick 2 papers, process both, then compare.

    Args:
        query: Search keyword or topic.
    """
    console.print("\n[bold yellow]⚖️  Compare Mode: You will pick 2 papers to compare.[/bold yellow]")

    # Search once — pick Paper 1
    console.print("\n[bold]Step 1/6 → Searching ArXiv...[/bold]")
    papers = search_papers(query, max_results=5)
    if not papers:
        sys.exit(1)

    console.print("\n[bold]Step 2/6 → Pick Paper 1...[/bold]")
    display_papers(papers)
    paper1 = pick_paper(papers)

    # Pick Paper 2 from same results (different choice)
    console.print("\n[bold]Step 3/6 → Pick Paper 2 (choose a different one)...[/bold]")
    remaining = [p for p in papers if p["index"] != paper1["index"]]
    # Re-index remaining papers for clean display
    for i, p in enumerate(remaining, start=1):
        p["index"] = i
    display_papers(remaining)
    paper2 = pick_paper(remaining)

    # Process Paper 1
    console.print("\n[bold]Step 4/6 → Processing Paper 1...[/bold]")
    summary1, extraction1, _ = process_single_paper(paper1, "Paper 1")

    # Process Paper 2
    console.print("\n[bold]Step 5/6 → Processing Paper 2...[/bold]")
    summary2, extraction2, _ = process_single_paper(paper2, "Paper 2")

    # Compare
    console.print("\n[bold]Step 6/6 → Running Comparison Agent...[/bold]")
    comparison = compare_papers(
        title1=paper1["title"],
        extraction1=extraction1,
        title2=paper2["title"],
        extraction2=extraction2
    )
    display_comparison(comparison)

    # Save
    output_path = save_comparison_report(comparison, paper1["title"], paper2["title"])
    console.print(f"\n[bold green]💾 Comparison report saved to:[/bold green] {output_path}")



def run_pdf_mode(pdf_path: str):
    """
    Phase 1+3 mode: Directly summarize and extract from a local PDF file.

    Args:
        pdf_path: Path to the PDF file.
    """
    if not os.path.exists(pdf_path):
        console.print(f"[bold red]❌ File not found:[/bold red] {pdf_path}")
        sys.exit(1)

    if not pdf_path.lower().endswith(".pdf"):
        console.print("[bold red]❌ Please provide a valid .pdf file.[/bold red]")
        sys.exit(1)

    console.print("\n[bold]Step 1/4 → Extracting text from PDF...[/bold]")
    text = extract_text_from_pdf(pdf_path)

    console.print("\n[bold]Step 2/4 → Preparing text for LLM...[/bold]")
    chunks = chunk_text(text, max_chars=12000)

    console.print("\n[bold]Step 3/4 → Generating summary with Groq...[/bold]")
    summary = summarize_long_paper(chunks)
    console.print("\n")
    console.print(Panel(Markdown(summary), title="📄 Paper Summary", border_style="green"))

    console.print("\n[bold]Step 4/4 → Extracting methodology details...[/bold]")
    extraction = extract_from_chunks(chunks)
    display_extraction(extraction)

    title = os.path.splitext(os.path.basename(pdf_path))[0]
    output_path = save_full_report(summary, extraction, title)
    console.print(f"\n[bold green]💾 Full report saved to:[/bold green] {output_path}")


def run_search_mode(query: str):
    """
    Phase 2+3 mode: Search ArXiv, pick a paper, download, summarize and extract.

    Args:
        query: Search keyword or topic.
    """
    # Step 1: Search ArXiv
    console.print("\n[bold]Step 1/5 → Searching ArXiv...[/bold]")
    papers = search_papers(query, max_results=5)

    if not papers:
        sys.exit(1)

    # Step 2: Display results and let user pick
    console.print("\n[bold]Step 2/5 → Select a paper...[/bold]")
    display_papers(papers)
    selected_paper = pick_paper(papers)

    # Step 3: Download the PDF
    console.print("\n[bold]Step 3/5 → Downloading PDF...[/bold]")
    pdf_path = download_pdf(selected_paper)

    # Step 4: Summarize
    console.print("\n[bold]Step 4/5 → Summarizing paper...[/bold]")
    text = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(text, max_chars=12000)
    summary = summarize_long_paper(chunks)
    console.print("\n")
    console.print(Panel(Markdown(summary), title="📄 Paper Summary", border_style="green"))

    # Step 5: Extract methodology
    console.print("\n[bold]Step 5/5 → Extracting methodology details...[/bold]")
    extraction = extract_from_chunks(chunks)
    display_extraction(extraction)

    output_path = save_full_report(summary, extraction, selected_paper["title"])
    console.print(f"\n[bold green]💾 Full report saved to:[/bold green] {output_path}")


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
    group.add_argument(
        "--compare",
        type=str,
        metavar="QUERY",
        help="Search ArXiv and compare 2 papers side by side"
    )

    args = parser.parse_args()

    console.print(Panel.fit(
        "[bold magenta]🔬 Research Agent[/bold magenta]\n"
        "[dim]Powered by Groq + LLaMA 3 + ArXiv[/dim]",
        border_style="magenta"
    ))

    if args.search:
        run_search_mode(args.search)
    elif args.compare:
        run_compare_mode(args.compare)
    elif args.pdf:
        run_pdf_mode(args.pdf)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()