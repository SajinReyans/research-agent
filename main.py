import os
import sys
import argparse
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from agent.parser import extract_text_from_pdf, chunk_text
from agent.summarizer import summarize_long_paper

console = Console()


def save_summary(summary: str, pdf_path: str) -> str:
    """
    Saves the summary to the outputs folder as a markdown file.

    Args:
        summary: The generated summary text.
        pdf_path: Original PDF path (used to name the output file).

    Returns:
        Path to saved summary file.
    """
    os.makedirs("outputs", exist_ok=True)

    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"outputs/{base_name}_summary_{timestamp}.md"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# Summary: {base_name}\n")
        f.write(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        f.write("---\n\n")
        f.write(summary)

    return output_path


def run(pdf_path: str):
    """
    Main pipeline: PDF → Parse → Chunk → Summarize → Save.

    Args:
        pdf_path: Path to the research paper PDF.
    """
    console.print(Panel.fit(
        "[bold magenta]🔬 Research Agent — PDF Summarizer[/bold magenta]\n"
        "[dim]Powered by Groq + LLaMA 3[/dim]",
        border_style="magenta"
    ))

    # Step 1: Validate file
    if not os.path.exists(pdf_path):
        console.print(f"[bold red]❌ File not found:[/bold red] {pdf_path}")
        sys.exit(1)

    if not pdf_path.lower().endswith(".pdf"):
        console.print("[bold red]❌ Please provide a valid .pdf file.[/bold red]")
        sys.exit(1)

    # Step 2: Extract text from PDF
    console.print("\n[bold]Step 1/3 → Extracting text from PDF...[/bold]")
    text = extract_text_from_pdf(pdf_path)

    # Step 3: Chunk the text (handles long papers)
    console.print("\n[bold]Step 2/3 → Preparing text for LLM...[/bold]")
    chunks = chunk_text(text, max_chars=12000)

    # Step 4: Generate summary
    console.print("\n[bold]Step 3/3 → Generating summary with Groq...[/bold]")
    summary = summarize_long_paper(chunks)

    # Step 5: Display summary
    console.print("\n")
    console.print(Panel(Markdown(summary), title="📄 Paper Summary", border_style="green"))

    # Step 6: Save to file
    output_path = save_summary(summary, pdf_path)
    console.print(f"\n[bold green]💾 Summary saved to:[/bold green] {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Research Agent: Summarize a research paper PDF using Groq LLM"
    )
    parser.add_argument(
        "pdf",
        type=str,
        help="Path to the research paper PDF file"
    )
    args = parser.parse_args()
    run(args.pdf)


if __name__ == "__main__":
    main()
