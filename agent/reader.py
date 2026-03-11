import os
from groq import Groq
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from agent.prompts import EXTRACTION_PROMPT

load_dotenv()
console = Console()

GROQ_MODEL = "llama-3.3-70b-versatile"


def get_groq_client() -> Groq:
    """
    Initializes and returns the Groq client.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found. Please set it in your .env file.")
    return Groq(api_key=api_key)


def extract_methodology(text: str) -> str:
    """
    Sends paper text to Groq and extracts structured methodology details.

    Args:
        text: Cleaned paper text.

    Returns:
        Structured extraction report as a string.
    """
    client = get_groq_client()
    prompt = EXTRACTION_PROMPT.format(paper_text=text)

    console.print(f"[bold cyan]🔍 Reader Agent extracting methodology ({GROQ_MODEL})...[/bold cyan]")

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert AI research analyst. Extract structured technical details from research papers with precision."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,    # Very low — we want factual extraction only
            max_tokens=2000,
        )

        extraction = response.choices[0].message.content
        console.print("[bold green]✅ Extraction complete![/bold green]")
        return extraction

    except Exception as e:
        console.print(f"[bold red]❌ Reader Agent error:[/bold red] {e}")
        raise


def extract_from_chunks(chunks: list[str]) -> str:
    """
    Handles extraction for long papers by extracting from the most
    relevant chunk (first 2 chunks usually contain methodology).

    Args:
        chunks: List of text chunks.

    Returns:
        Extraction report string.
    """
    if len(chunks) == 1:
        return extract_methodology(chunks[0])

    console.print(f"[bold yellow]📚 Long paper: extracting from first 2 chunks for best accuracy...[/bold yellow]")

    # Use first 2 chunks — methodology is usually in early sections
    combined = "\n\n".join(chunks[:2])
    return extract_methodology(combined)


def display_extraction(extraction: str):
    """
    Displays the extraction report in the terminal.

    Args:
        extraction: Structured extraction report string.
    """
    console.print("\n")
    console.print(Panel(
        Markdown(extraction),
        title="🔬 Reader Agent — Methodology Extraction",
        border_style="blue"
    ))