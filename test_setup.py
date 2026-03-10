"""
Run this file first to verify all dependencies are installed correctly.
Usage: python test_setup.py
"""

def test_imports():
    errors = []

    try:
        import fitz
        print("✅ PyMuPDF (fitz) — OK")
    except ImportError:
        errors.append("❌ PyMuPDF missing — run: pip install pymupdf")

    try:
        import groq
        print("✅ Groq SDK — OK")
    except ImportError:
        errors.append("❌ Groq missing — run: pip install groq")

    try:
        import langchain
        print("✅ LangChain — OK")
    except ImportError:
        errors.append("❌ LangChain missing — run: pip install langchain")

    try:
        import dotenv
        print("✅ python-dotenv — OK")
    except ImportError:
        errors.append("❌ python-dotenv missing — run: pip install python-dotenv")

    try:
        import tiktoken
        print("✅ tiktoken — OK")
    except ImportError:
        errors.append("❌ tiktoken missing — run: pip install tiktoken")

    try:
        import rich
        print("✅ rich — OK")
    except ImportError:
        errors.append("❌ rich missing — run: pip install rich")

    try:
        import tqdm
        print("✅ tqdm — OK")
    except ImportError:
        errors.append("❌ tqdm missing — run: pip install tqdm")

    print("\n" + "="*40)

    if errors:
        print("⚠️  Some libraries are missing:\n")
        for e in errors:
            print(f"  {e}")
        print("\nRun this to fix all at once:")
        print("  pip install groq pymupdf langchain langchain-groq python-dotenv tiktoken tqdm rich")
    else:
        print("🎉 All dependencies installed! You're ready to go.")
        print("\nNext step:")
        print("  1. Add your GROQ_API_KEY to the .env file")
        print("  2. Run: python main.py your_paper.pdf")


def test_env():
    import os
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        print("\n⚠️  GROQ_API_KEY not set in .env file.")
        print("   → Copy .env.example to .env and add your key.")
    else:
        print(f"\n✅ GROQ_API_KEY found (starts with: {api_key[:8]}...)")


if __name__ == "__main__":
    print("🔍 Checking dependencies...\n")
    test_imports()
    test_env()