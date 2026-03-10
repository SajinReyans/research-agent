import fitz  # PyMuPDF
from rich.console import Console

console = Console()

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts and cleans text from a PDF file.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Cleaned text string extracted from the PDF.
    """
    console.print(f"[bold cyan]📄 Loading PDF:[/bold cyan] {pdf_path}")

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        console.print(f"[bold red]❌ Failed to open PDF:[/bold red] {e}")
        raise

    full_text = []

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text")
        if text.strip():
            full_text.append(text)

    doc.close()

    if not full_text:
        raise ValueError("No text could be extracted from the PDF. It may be scanned or image-based.")

    raw_text = "\n".join(full_text)
    cleaned_text = clean_text(raw_text)

    console.print(f"[bold green]✅ Extracted {len(cleaned_text)} characters from {len(full_text)} pages.[/bold green]")
    return cleaned_text


def clean_text(text: str) -> str:
    """
    Cleans raw extracted PDF text.

    Args:
        text: Raw text from PDF.

    Returns:
        Cleaned text.
    """
    import re

    # Remove excessive whitespace and newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)

    # Remove page numbers (common pattern: lone digits on a line)
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def chunk_text(text: str, max_chars: int = 12000) -> list[str]:
    """
    Splits text into chunks to avoid exceeding LLM token limits.

    Args:
        text: Full paper text.
        max_chars: Max characters per chunk.

    Returns:
        List of text chunks.
    """
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        current_length += len(word) + 1
        current_chunk.append(word)

        if current_length >= max_chars:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_length = 0

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    console.print(f"[bold yellow]📦 Split into {len(chunks)} chunk(s) for processing.[/bold yellow]")
    return chunks