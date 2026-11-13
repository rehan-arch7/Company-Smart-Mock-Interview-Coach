"""
One-shot setup script for MockMentor AI.
Run this once to: generate seed data + build the ChromaDB vector store.
"""
import sys
import io
from pathlib import Path

# Fix Windows console encoding for Unicode/emoji characters
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

print("=" * 60)
print("  MockMentor AI --- Setup Script")
print("=" * 60)

print("\n[Step 1] Generating synthetic question & feedback bank...")
from data.seed_data import save_seed_data
questions, feedbacks = save_seed_data()

print("\n[Step 2] Building ChromaDB vector store...")
from vectorstore.chroma_setup import setup_vectorstore
setup_vectorstore()

print("\n" + "=" * 60)
print("Setup complete! You can now run the app:")
print("   streamlit run app.py")
print("=" * 60)
