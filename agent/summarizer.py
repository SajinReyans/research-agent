import os
from groq import Groq
from dotenv import load_dotenv
from rich.console import Console
from agent.prompts import SUMMARY_PROMPT

load_dotenv()
console = Console()

# Available Groq models (fast & free)
GROQ_MODEL = "llama-3.1-8b-instant"  # Can switch to "llama-3.3-70b-versatile" for better quality


def get_groq_client() -> Groq:
    """
    Initializes and returns the Groq client.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found. Please set it in your .env file.")
    return Groq(api_key=api_key)


def summarize_text(text: str) -> str:
    """
    Sends paper text to Groq LLM and returns a structured summary.

    Args:
        text: Cleaned paper text.

    Returns:
        Structured summary string.
    """
    client = get_groq_client()

    # Truncate to ~3000 chars to stay within free tier TPM limits
    truncated_text = text[:3000]
    prompt = SUMMARY_PROMPT.format(paper_text=truncated_text)

    console.print(f"[bold cyan]🤖 Sending to Groq ({GROQ_MODEL})...[/bold cyan]")

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert AI research assistant that summarizes academic papers clearly and accurately."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,       # Lower = more factual, less creative
            max_tokens=800,
        )

        summary = response.choices[0].message.content
        console.print("[bold green]✅ Summary generated successfully![/bold green]")
        return summary

    except Exception as e:
        console.print(f"[bold red]❌ Groq API error:[/bold red] {e}")
        raise


def summarize_long_paper(chunks: list[str]) -> str:
    """
    Handles summarization for long papers by summarizing chunks
    and then combining them into one final summary.

    Args:
        chunks: List of text chunks.

    Returns:
        Final combined summary.
    """
    if len(chunks) == 1:
        return summarize_text(chunks[0])

    console.print(f"[bold yellow]📚 Long paper detected. Summarizing {len(chunks)} chunks...[/bold yellow]")

    chunk_summaries = []
    for i, chunk in enumerate(chunks, start=1):
        console.print(f"[dim]  → Chunk {i}/{len(chunks)}[/dim]")
        summary = summarize_text(chunk)
        chunk_summaries.append(summary)

    # Combine all chunk summaries into one final summary
    combined = "\n\n---\n\n".join(chunk_summaries)
    console.print("[bold cyan]🔗 Combining chunk summaries into final report...[/bold cyan]")

    final_summary = summarize_text(
        f"The following are partial summaries of a long research paper. "
        f"Combine them into one clean, unified summary:\n\n{combined}"
    )

    return final_summary