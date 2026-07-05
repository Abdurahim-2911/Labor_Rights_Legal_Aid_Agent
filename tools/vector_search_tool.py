"""
Vector Search Tool

Queries the local ChromaDB vector store for relevant legal text chunks.
Called by the orchestrator's search_legal_docs node (not by an LLM agent directly).
"""

import os
import chromadb


def search_legal_corpus(query: str, top_k: int = 5) -> list[dict]:
    """Search the UAE labour law corpus for relevant legal text chunks.

    Args:
        query: The legal situation or question to search for.
        top_k: Number of results to return.

    Returns:
        List of dicts with keys: 'text', 'article_number', 'source_doc'.
        Returns an empty list if the database is not available.
    """
    try:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        db_path = os.path.join(base_dir, "data", "chroma_db")
        client = chromadb.PersistentClient(path=db_path)
        # Use ChromaDB's default embedding (sentence-transformers) for local embeddings
        collection = client.get_collection(name="legal_corpus")

        results = collection.query(query_texts=[query], n_results=top_k)

        output = []
        if results and results.get("documents"):
            docs = results["documents"][0]
            metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)

            for doc, meta in zip(docs, metas):
                output.append({
                    "text": doc,
                    "article_number": meta.get("article_number", "Unknown"),
                    "source_doc": meta.get("source_doc", "Unknown"),
                })
        return output

    except Exception as e:
        print(f"ChromaDB query error: {e}")
        return []
