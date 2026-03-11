import os
import chromadb
from chromadb.utils import embedding_functions
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich import box

console = Console()

# Local ChromaDB storage path
CHROMA_DB_PATH = "chroma_db"
COLLECTION_NAME = "literature_reviews"


def get_collection():
    """
    Initializes ChromaDB client and returns the literature reviews collection.

    Returns:
        ChromaDB collection object.
    """
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

    # Use sentence transformers for embeddings (runs locally, no API key needed)
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
        metadata={"description": "Stored literature reviews from research agent"}
    )

    return collection


def save_review_to_memory(
    topic: str,
    review: str,
    title1: str,
    title2: str
) -> bool:
    """
    Saves a literature review to ChromaDB memory.

    Args:
        topic: The research topic/query.
        review: Full literature review text.
        title1: Title of Paper 1.
        title2: Title of Paper 2.

    Returns:
        True if saved successfully, False otherwise.
    """
    try:
        collection = get_collection()

        # Create unique ID from topic + timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        doc_id = f"{topic.replace(' ', '_')}_{timestamp}"

        # Store review with metadata
        collection.add(
            documents=[review],
            metadatas=[{
                "topic": topic,
                "title1": title1,
                "title2": title2,
                "timestamp": timestamp,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }],
            ids=[doc_id]
        )

        console.print(f"[bold green]🧠 Saved to memory:[/bold green] topic='{topic}' | id={doc_id}")
        return True

    except Exception as e:
        console.print(f"[bold red]❌ Memory save error:[/bold red] {e}")
        return False


def search_memory(query: str, n_results: int = 3) -> list[dict]:
    """
    Searches ChromaDB for past literature reviews similar to the query.

    Args:
        query: Search topic or question.
        n_results: Number of results to return.

    Returns:
        List of matching review dicts with content and metadata.
    """
    try:
        collection = get_collection()

        # Check if collection has any documents
        count = collection.count()
        if count == 0:
            console.print("[bold yellow]⚠️  No reviews in memory yet.[/bold yellow]")
            return []

        # Adjust n_results if fewer documents exist
        n_results = min(n_results, count)

        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )

        if not results["documents"] or not results["documents"][0]:
            console.print("[bold yellow]⚠️  No matching reviews found in memory.[/bold yellow]")
            return []

        matches = []
        for i, doc in enumerate(results["documents"][0]):
            matches.append({
                "id": results["ids"][0][i],
                "review": doc,
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i]
            })

        return matches

    except Exception as e:
        console.print(f"[bold red]❌ Memory search error:[/bold red] {e}")
        return []


def check_existing_review(topic: str, threshold: float = 0.3) -> dict | None:
    """
    Checks if a very similar review already exists in memory.
    Used to avoid re-downloading and re-processing papers.

    Args:
        topic: The research topic to check.
        threshold: Similarity threshold (lower = more similar).

    Returns:
        Existing review dict if found, None otherwise.
    """
    try:
        collection = get_collection()

        if collection.count() == 0:
            return None

        results = collection.query(
            query_texts=[topic],
            n_results=1
        )

        if not results["documents"] or not results["documents"][0]:
            return None

        distance = results["distances"][0][0]

        if distance < threshold:
            metadata = results["metadatas"][0][0]
            console.print(f"\n[bold yellow]🧠 Found existing review in memory![/bold yellow]")
            console.print(f"[dim]  Topic: {metadata['topic']}[/dim]")
            console.print(f"[dim]  Papers: {metadata['title1'][:40]}... & {metadata['title2'][:40]}...[/dim]")
            console.print(f"[dim]  Date: {metadata['date']}[/dim]")
            console.print(f"[dim]  Similarity score: {1 - distance:.2f}[/dim]")
            return {
                "review": results["documents"][0][0],
                "metadata": metadata
            }

        return None

    except Exception as e:
        console.print(f"[bold red]❌ Memory check error:[/bold red] {e}")
        return None


def display_memory_results(matches: list[dict]):
    """
    Displays memory search results in the terminal.

    Args:
        matches: List of matching review dicts.
    """
    if not matches:
        console.print("[bold yellow]No results found in memory.[/bold yellow]")
        return

    console.print(f"\n[bold cyan]🧠 Found {len(matches)} review(s) in memory:[/bold cyan]\n")

    for i, match in enumerate(matches, start=1):
        meta = match["metadata"]
        similarity = 1 - match["distance"]

        # Show metadata summary
        table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
        table.add_column("Key", style="bold cyan", width=15)
        table.add_column("Value", style="white")

        table.add_row("Topic", meta.get("topic", "N/A"))
        table.add_row("Paper 1", meta.get("title1", "N/A")[:70])
        table.add_row("Paper 2", meta.get("title2", "N/A")[:70])
        table.add_row("Date", meta.get("date", "N/A"))
        table.add_row("Similarity", f"{similarity:.0%}")

        console.print(Panel(
            table,
            title=f"[bold]Result {i}[/bold]",
            border_style="cyan"
        ))

        # Ask if user wants to see full review
        show = input(f"\n👉 View full review #{i}? (y/n): ").strip().lower()
        if show == "y":
            console.print(Panel(
                Markdown(match["review"]),
                title=f"📝 Literature Review — {meta.get('topic', '')}",
                border_style="green"
            ))


def clear_memory() -> bool:
    """
    Clears all stored reviews from ChromaDB.

    Returns:
        True if cleared successfully.
    """
    try:
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        client.delete_collection(COLLECTION_NAME)
        console.print("[bold green]✅ Memory cleared successfully![/bold green]")
        return True

    except Exception as e:
        console.print(f"[bold red]❌ Memory clear error:[/bold red] {e}")
        return False


def get_memory_stats() -> dict:
    """
    Returns stats about the current memory state.

    Returns:
        Dict with count and collection info.
    """
    try:
        collection = get_collection()
        count = collection.count()
        return {"total_reviews": count}
    except Exception as e:
        return {"total_reviews": 0, "error": str(e)}