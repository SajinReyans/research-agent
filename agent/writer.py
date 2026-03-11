import os
from groq import Groq
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from agent.prompts import REVIEW_PROMPT

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


def generate_literature_review(
    topic: str,
    title1: str,
    summary1: str,
    extraction1: str,
    title2: str,
    summary2: str,
    extraction2: str,
    comparison: str
) -> str:
    """
    Generates a full academic literature review from two papers.

    Args:
        topic: The research topic/query.
        title1: Title of Paper 1.
        summary1: Summary of Paper 1.
        extraction1: Extraction report of Paper 1.
        title2: Title of Paper 2.
        summary2: Summary of Paper 2.
        extraction2: Extraction report of Paper 2.
        comparison: Comparison report of both papers.

    Returns:
        Full literature review as a markdown string.
    """
    client = get_groq_client()

    prompt = REVIEW_PROMPT.format(
        topic=topic,
        title1=title1,
        summary1=summary1,
        extraction1=extraction1,
        title2=title2,
        summary2=summary2,
        extraction2=extraction2,
        comparison=comparison
    )

    console.print(f"\n[bold cyan]✍️  Writer Agent generating literature review...[/bold cyan]")
    console.print(f"[dim]  Topic: {topic}[/dim]")
    console.print(f"[dim]  Paper 1: {title1[:60]}{'...' if len(title1) > 60 else ''}[/dim]")
    console.print(f"[dim]  Paper 2: {title2[:60]}{'...' if len(title2) > 60 else ''}[/dim]")

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert academic writer specializing in AI and computer science. "
                        "You write clear, analytical, and well-structured literature reviews in formal academic style."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4,    # Slightly higher for more natural writing
            max_tokens=3000,
        )

        review = response.choices[0].message.content
        console.print("[bold green]✅ Literature review generated![/bold green]")
        return review

    except Exception as e:
        console.print(f"[bold red]❌ Writer Agent error:[/bold red] {e}")
        raise


def display_review(review: str):
    """
    Displays the literature review in the terminal.

    Args:
        review: Full literature review string.
    """
    console.print("\n")
    console.print(Panel(
        Markdown(review),
        title="📝 Writer Agent — Literature Review",
        border_style="cyan"
    ))