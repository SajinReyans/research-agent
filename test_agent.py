"""
Research Agent — Full Test Suite
Tests all 6 phases of the research agent.

Usage: python test_agent.py
"""

import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()

# ─────────────────────────────────────────────
# TEST RESULTS TRACKER
# ─────────────────────────────────────────────
results = []

def record(phase: str, test: str, passed: bool, note: str = ""):
    results.append({
        "phase": phase,
        "test": test,
        "passed": passed,
        "note": note
    })
    status = "[bold green]✅ PASS[/bold green]" if passed else "[bold red]❌ FAIL[/bold red]"
    console.print(f"  {status} {test}" + (f" [dim]— {note}[/dim]" if note else ""))


# ─────────────────────────────────────────────
# PHASE 1: IMPORTS & ENVIRONMENT
# ─────────────────────────────────────────────
def test_phase1_imports():
    console.print("\n[bold magenta]── Phase 1: Imports & Environment ──[/bold magenta]")

    # Test all library imports
    libs = {
        "fitz (PyMuPDF)": "import fitz",
        "groq": "import groq",
        "langchain": "import langchain",
        "dotenv": "import dotenv",
        "tiktoken": "import tiktoken",
        "rich": "import rich",
        "tqdm": "import tqdm",
        "arxiv": "import arxiv",
        "chromadb": "import chromadb",
        "sentence_transformers": "import sentence_transformers",
    }

    for name, stmt in libs.items():
        try:
            exec(stmt)
            record("Phase 1", f"Import {name}", True)
        except ImportError as e:
            record("Phase 1", f"Import {name}", False, str(e))

    # Test .env and API key
    try:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        if api_key and api_key != "your_groq_api_key_here":
            record("Phase 1", "GROQ_API_KEY loaded", True, f"starts with {api_key[:8]}...")
        else:
            record("Phase 1", "GROQ_API_KEY loaded", False, "Key missing or placeholder in .env")
    except Exception as e:
        record("Phase 1", "GROQ_API_KEY loaded", False, str(e))

    # Test agent module imports
    agent_modules = {
        "agent.parser": "from agent.parser import extract_text_from_pdf, chunk_text",
        "agent.summarizer": "from agent.summarizer import summarize_long_paper",
        "agent.searcher": "from agent.searcher import search_papers",
        "agent.downloader": "from agent.downloader import download_pdf",
        "agent.reader": "from agent.reader import extract_from_chunks",
        "agent.comparator": "from agent.comparator import compare_papers",
        "agent.writer": "from agent.writer import generate_literature_review",
        "agent.memory": "from agent.memory import save_review_to_memory, search_memory",
    }

    for name, stmt in agent_modules.items():
        try:
            exec(stmt)
            record("Phase 1", f"Module {name}", True)
        except Exception as e:
            record("Phase 1", f"Module {name}", False, str(e))


# ─────────────────────────────────────────────
# PHASE 2: PDF PARSER
# ─────────────────────────────────────────────
def test_phase2_parser():
    console.print("\n[bold magenta]── Phase 2: PDF Parser ──[/bold magenta]")

    from agent.parser import clean_text, chunk_text

    # Test clean_text
    try:
        raw = "Hello   World\n\n\n\nTest   123\n\n\n"
        cleaned = clean_text(raw)
        assert "   " not in cleaned, "Multiple spaces not cleaned"
        assert cleaned.count("\n\n\n") == 0, "Triple newlines not cleaned"
        record("Phase 2", "clean_text removes extra whitespace", True)
    except Exception as e:
        record("Phase 2", "clean_text removes extra whitespace", False, str(e))

    # Test chunk_text
    try:
        long_text = "word " * 5000
        chunks = chunk_text(long_text, max_chars=1000)
        assert len(chunks) > 1, "Long text should produce multiple chunks"
        assert all(len(c) <= 1100 for c in chunks), "Chunks exceed max size"
        record("Phase 2", "chunk_text splits long text correctly", True, f"{len(chunks)} chunks")
    except Exception as e:
        record("Phase 2", "chunk_text splits long text correctly", False, str(e))

    # Test PDF extraction on a real file if exists
    pdf_files = [f for f in os.listdir(".") if f.endswith(".pdf")]
    if pdf_files:
        try:
            from agent.parser import extract_text_from_pdf
            text = extract_text_from_pdf(pdf_files[0])
            assert len(text) > 100, "Extracted text too short"
            record("Phase 2", f"PDF extraction from {pdf_files[0]}", True, f"{len(text)} chars")
        except Exception as e:
            record("Phase 2", f"PDF extraction from {pdf_files[0]}", False, str(e))
    else:
        record("Phase 2", "PDF extraction (no PDF found)", True, "Skipped — no PDF in folder")


# ─────────────────────────────────────────────
# PHASE 3: GROQ API CONNECTION
# ─────────────────────────────────────────────
def test_phase3_groq():
    console.print("\n[bold magenta]── Phase 3: Groq API Connection ──[/bold magenta]")

    try:
        from dotenv import load_dotenv
        load_dotenv()
        from groq import Groq

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "your_groq_api_key_here":
            record("Phase 3", "Groq API ping", False, "No API key set")
            return

        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "Say hello in 3 words."}],
            max_tokens=20
        )
        reply = response.choices[0].message.content
        assert len(reply) > 0
        record("Phase 3", "Groq API ping", True, f"Response: '{reply.strip()}'")

    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg:
            record("Phase 3", "Groq API ping", False, "Rate limit hit — wait and retry")
        elif "401" in error_msg:
            record("Phase 3", "Groq API ping", False, "Invalid API key")
        else:
            record("Phase 3", "Groq API ping", False, error_msg[:80])


# ─────────────────────────────────────────────
# PHASE 4: ARXIV SEARCH
# ─────────────────────────────────────────────
def test_phase4_arxiv():
    console.print("\n[bold magenta]── Phase 4: ArXiv Search ──[/bold magenta]")

    try:
        from agent.searcher import search_papers
        papers = search_papers("transformer architecture", max_results=3)
        assert len(papers) > 0, "No papers returned"
        assert "title" in papers[0], "Missing title field"
        assert "pdf_url" in papers[0], "Missing pdf_url field"
        assert "authors" in papers[0], "Missing authors field"
        assert "published" in papers[0], "Missing published field"
        record("Phase 4", "ArXiv search returns results", True, f"{len(papers)} papers found")
        record("Phase 4", "Paper metadata complete", True, f"title, authors, date, pdf_url present")
    except Exception as e:
        record("Phase 4", "ArXiv search", False, str(e))


# ─────────────────────────────────────────────
# PHASE 5: CHROMADB MEMORY
# ─────────────────────────────────────────────
def test_phase5_memory():
    console.print("\n[bold magenta]── Phase 5: ChromaDB Memory ──[/bold magenta]")

    try:
        from agent.memory import (
            save_review_to_memory,
            search_memory,
            check_existing_review,
            get_memory_stats,
            clear_memory
        )

        # Test save
        saved = save_review_to_memory(
            topic="test transformers",
            review="# Test Review\nThis is a test literature review about transformers.",
            title1="Attention Is All You Need",
            title2="BERT: Pre-training of Deep Bidirectional Transformers"
        )
        assert saved, "Save returned False"
        record("Phase 5", "Save review to ChromaDB", True)

        # Test stats
        stats = get_memory_stats()
        assert stats["total_reviews"] >= 1
        record("Phase 5", "Get memory stats", True, f"{stats['total_reviews']} review(s) stored")

        # Test search
        matches = search_memory("transformers", n_results=1)
        assert len(matches) > 0, "No results returned from search"
        assert "review" in matches[0], "Missing review field"
        assert "metadata" in matches[0], "Missing metadata field"
        record("Phase 5", "Search memory by topic", True, f"{len(matches)} result(s) found")

        # Test duplicate check
        existing = check_existing_review("test transformers", threshold=0.5)
        assert existing is not None, "Should find existing review"
        record("Phase 5", "Duplicate check finds existing review", True)

        # Test clear
        cleared = clear_memory()
        assert cleared, "Clear returned False"
        stats_after = get_memory_stats()
        assert stats_after["total_reviews"] == 0
        record("Phase 5", "Clear memory works", True, "All reviews deleted")

    except Exception as e:
        record("Phase 5", "ChromaDB memory operations", False, str(e))


# ─────────────────────────────────────────────
# PHASE 6: OUTPUTS FOLDER
# ─────────────────────────────────────────────
def test_phase6_outputs():
    console.print("\n[bold magenta]── Phase 6: Output Files ──[/bold magenta]")

    # Check outputs folder exists or can be created
    try:
        os.makedirs("outputs", exist_ok=True)
        assert os.path.exists("outputs")
        record("Phase 6", "outputs/ folder exists", True)
    except Exception as e:
        record("Phase 6", "outputs/ folder exists", False, str(e))

    # Check downloads folder
    try:
        os.makedirs("downloads", exist_ok=True)
        assert os.path.exists("downloads")
        record("Phase 6", "downloads/ folder exists", True)
    except Exception as e:
        record("Phase 6", "downloads/ folder exists", False, str(e))

    # Count existing outputs
    md_files = [f for f in os.listdir("outputs") if f.endswith(".md")] if os.path.exists("outputs") else []
    record("Phase 6", "Existing output files", True, f"{len(md_files)} .md file(s) in outputs/")

    # Count downloaded PDFs
    pdfs = [f for f in os.listdir("downloads") if f.endswith(".pdf")] if os.path.exists("downloads") else []
    record("Phase 6", "Downloaded PDFs", True, f"{len(pdfs)} PDF(s) in downloads/")


# ─────────────────────────────────────────────
# PRINT FINAL REPORT
# ─────────────────────────────────────────────
def print_report():
    console.print("\n")
    console.print(Panel.fit(
        "[bold white]📊 Test Results Summary[/bold white]",
        border_style="magenta"
    ))

    table = Table(box=box.ROUNDED, show_lines=True, header_style="bold magenta")
    table.add_column("Phase", style="bold cyan", width=12)
    table.add_column("Test", style="white", min_width=40)
    table.add_column("Status", justify="center", width=10)
    table.add_column("Note", style="dim", min_width=25)

    passed = 0
    failed = 0

    for r in results:
        status = "[bold green]✅ PASS[/bold green]" if r["passed"] else "[bold red]❌ FAIL[/bold red]"
        table.add_row(r["phase"], r["test"], status, r["note"])
        if r["passed"]:
            passed += 1
        else:
            failed += 1

    console.print(table)

    total = passed + failed
    console.print(f"\n[bold]Results:[/bold] {passed}/{total} tests passed", end="  ")

    if failed == 0:
        console.print("[bold green]🎉 All tests passed! Your agent is fully operational.[/bold green]")
    elif failed <= 2:
        console.print(f"[bold yellow]⚠️  {failed} test(s) failed. Check the notes above.[/bold yellow]")
    else:
        console.print(f"[bold red]❌ {failed} test(s) failed. Please fix the issues above.[/bold red]")

    console.print("\n[bold]Next steps:[/bold]")
    if failed == 0:
        console.print("  → Run: [bold]python main.py --review \"vision transformers\"[/bold]")
        console.print("  → Then: [bold]python main.py --memory \"vision transformers\"[/bold]")
    else:
        console.print("  → Fix the failed tests above")
        console.print("  → Re-run: [bold]python test_agent.py[/bold]")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    console.print(Panel.fit(
        "[bold magenta]🔬 Research Agent — Test Suite[/bold magenta]\n"
        "[dim]Testing all 6 phases...[/dim]",
        border_style="magenta"
    ))

    test_phase1_imports()
    test_phase2_parser()
    test_phase3_groq()
    test_phase4_arxiv()
    test_phase5_memory()
    test_phase6_outputs()
    print_report()