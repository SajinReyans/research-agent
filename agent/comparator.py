import os
from groq import Groq
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from agent.prompts import COMPARISON_PROMPT

load_dotenv()
console = Console()

GROQ_MODEL = "llama-3.1-8b-instant"


def get_groq_client() -> Groq:
    """
    Initializes and returns the Groq client.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found. Please set it in your .env file.")
    return Groq(api_key=api_key)


def compare_papers(
    title1: str,
    extraction1: str,
    title2: str,
    extraction2: str
) -> str:
    """
    Compares two papers using their extraction reports.

    Args:
        title1: Title of Paper 1.
        extraction1: Structured extraction of Paper 1.
        title2: Title of Paper 2.
        extraction2: Structured extraction of Paper 2.

    Returns:
        Full comparison report as a string.
    """
    client = get_groq_client()

    prompt = COMPARISON_PROMPT.format(
        title1=title1,
        extraction1=extraction1,
        title2=title2,
        extraction2=extraction2
    )

    console.print(f"\n[bold cyan]⚖️  Comparison Agent comparing papers...[/bold cyan]")
    console.print(f"[dim]  📄 Paper 1: {title1[:60]}...[/dim]" if len(title1) > 60 else f"[dim]  📄 Paper 1: {title1}[/dim]")
    console.print(f"[dim]  📄 Paper 2: {title2[:60]}...[/dim]" if len(title2) > 60 else f"[dim]  📄 Paper 2: {title2}[/dim]")

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert AI research analyst specializing in comparing and contrasting research papers objectively and thoroughly."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=2500,
        )

        comparison = response.choices[0].message.content
        console.print("[bold green]✅ Comparison complete![/bold green]")
        return comparison

    except Exception as e:
        console.print(f"[bold red]❌ Comparison Agent error:[/bold red] {e}")
        raise


def display_comparison(comparison: str):
    """
    Displays the comparison report in the terminal.

    Args:
        comparison: Full comparison report string.
    """
    console.print("\n")
    console.print(Panel(
        Markdown(comparison),
        title="⚖️  Comparison Agent — Side-by-Side Analysis",
        border_style="yellow"
    ))