"""
ChromaDB Vector Store Setup
Ingests seed data into two ChromaDB collections:
  - interview_questions
  - candidate_feedback
"""

import json
import sys
from pathlib import Path

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Add project root to path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

CHROMA_DIR = ROOT / "chroma_db"
DATA_DIR = ROOT / "data"


def get_chroma_client():
    """Return a persistent ChromaDB client."""
    return chromadb.PersistentClient(path=str(CHROMA_DIR))


def get_embedding_function():
    """Load local sentence-transformers model."""
    print("📦 Loading embedding model (sentence-transformers/all-MiniLM-L6-v2)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("✅ Embedding model loaded.")
    return model


class LocalEmbeddingFunction(chromadb.EmbeddingFunction):
    """ChromaDB-compatible local embedding function."""

    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def __call__(self, input):  # noqa: A002
        embeddings = self.model.encode(input, convert_to_numpy=True)
        return embeddings.tolist()


def ingest_questions(client: chromadb.PersistentClient, questions: list):
    """Ingest interview questions into ChromaDB."""
    ef = LocalEmbeddingFunction()

    # Delete existing collection if present
    try:
        client.delete_collection("interview_questions")
    except Exception:
        pass

    collection = client.create_collection(
        name="interview_questions",
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"}
    )

    batch_size = 100
    for i in range(0, len(questions), batch_size):
        batch = questions[i:i + batch_size]
        collection.add(
            ids=[q["id"] for q in batch],
            documents=[q["text"] for q in batch],
            metadatas=[{
                "company": q["company"],
                "role": q["role"],
                "year": q["year"],
                "difficulty": q["difficulty"],
                "tags": ", ".join(q["tags"]),
                "question": q["question"],
                "key_points": json.dumps(q["key_points"])
            } for q in batch]
        )
        print(f"  ↳ Ingested questions batch {i // batch_size + 1} ({len(batch)} items)")

    print(f"✅ Ingested {len(questions)} questions into 'interview_questions' collection.")
    return collection


def ingest_feedback(client: chromadb.PersistentClient, feedbacks: list):
    """Ingest candidate feedback into ChromaDB."""
    ef = LocalEmbeddingFunction()

    try:
        client.delete_collection("candidate_feedback")
    except Exception:
        pass

    collection = client.create_collection(
        name="candidate_feedback",
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"}
    )

    batch_size = 100
    for i in range(0, len(feedbacks), batch_size):
        batch = feedbacks[i:i + batch_size]
        collection.add(
            ids=[f["id"] for f in batch],
            documents=[f["text"] for f in batch],
            metadatas=[{
                "company": f["company"],
                "role": f["role"],
                "year": f["year"],
                "candidate_score": f["candidate_score"],
                "strengths": json.dumps(f["strengths"]),
                "gaps": json.dumps(f["gaps"]),
                "pattern_summary": f["pattern_summary"]
            } for f in batch]
        )
        print(f"  ↳ Ingested feedback batch {i // batch_size + 1} ({len(batch)} items)")

    print(f"✅ Ingested {len(feedbacks)} feedback entries into 'candidate_feedback' collection.")
    return collection


def setup_vectorstore():
    """Main setup function — run once to build the vector store."""
    print("\n🚀 Setting up ChromaDB vector store...\n")

    # Generate or load seed data
    q_path = DATA_DIR / "questions.json"
    f_path = DATA_DIR / "feedback.json"

    if not q_path.exists() or not f_path.exists():
        print("📝 Seed data not found. Generating...")
        from data.seed_data import save_seed_data
        questions, feedbacks = save_seed_data()
    else:
        print("📂 Loading existing seed data...")
        with open(q_path, encoding="utf-8") as f:
            questions = json.load(f)
        with open(f_path, encoding="utf-8") as f:
            feedbacks = json.load(f)
        print(f"  ↳ Loaded {len(questions)} questions, {len(feedbacks)} feedback entries")

    client = get_chroma_client()

    print("\n📊 Ingesting interview questions...")
    ingest_questions(client, questions)

    print("\n📊 Ingesting candidate feedback...")
    ingest_feedback(client, feedbacks)

    print("\n🎉 Vector store setup complete!")
    print(f"   Location: {CHROMA_DIR}")
    return client


def query_questions(company: str, role: str, n_results: int = 5) -> list[dict]:
    """Query relevant questions for a company + role."""
    client = get_chroma_client()
    ef = LocalEmbeddingFunction()

    collection = client.get_collection("interview_questions", embedding_function=ef)
    results = collection.query(
        query_texts=[f"{company} {role} interview questions"],
        n_results=min(n_results * 3, 30),
        where={"$and": [{"company": {"$eq": company}}, {"role": {"$eq": role}}]}
    )

    questions = []
    seen = set()
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        q_text = meta["question"]
        if q_text not in seen:
            seen.add(q_text)
            questions.append({
                "question": meta["question"],
                "key_points": json.loads(meta["key_points"]),
                "difficulty": meta["difficulty"],
                "tags": meta["tags"]
            })
        if len(questions) >= n_results:
            break

    return questions


def query_feedback(company: str, role: str, n_results: int = 5) -> list[dict]:
    """Query historical feedback patterns for a company + role."""
    client = get_chroma_client()
    ef = LocalEmbeddingFunction()

    collection = client.get_collection("candidate_feedback", embedding_function=ef)
    results = collection.query(
        query_texts=[f"{company} {role} candidate interview feedback patterns"],
        n_results=n_results,
        where={"$and": [{"company": {"$eq": company}}, {"role": {"$eq": role}}]}
    )

    feedbacks = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        feedbacks.append({
            "pattern_summary": meta["pattern_summary"],
            "strengths": json.loads(meta["strengths"]),
            "gaps": json.loads(meta["gaps"]),
            "candidate_score": meta["candidate_score"]
        })

    return feedbacks


if __name__ == "__main__":
    setup_vectorstore()
