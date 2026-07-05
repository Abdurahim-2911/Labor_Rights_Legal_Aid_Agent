"""
Ingest Corpus Script

Reads all PDF and TXT files from data/legal_corpus/, chunks them by article/section,
and stores them in a local ChromaDB vector store for RAG retrieval.

Usage (run from ANY directory):
    python scripts/ingest_corpus.py

The script automatically finds the correct data/ folder relative to its own location.
"""

import sys
import os

# --- Resolve absolute paths relative to THIS script's location ---
# This ensures the script works no matter which directory you run it from.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)  # Legal_Aid_Agent/

CORPUS_DIR = os.path.join(PROJECT_DIR, "data", "legal_corpus")
CHROMA_DIR = os.path.join(PROJECT_DIR, "data", "chroma_db")

sys.path.insert(0, PROJECT_DIR)

import glob
import chromadb
import fitz  # PyMuPDF: pip install pymupdf


def extract_text_from_pdf(file_path: str) -> str:
    """Extract all text from a PDF file using PyMuPDF."""
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text


def chunk_text(text: str, chunk_size: int = 600, overlap: int = 100) -> list[str]:
    """Split text into overlapping chunks for better retrieval.

    Args:
        text: The full document text.
        chunk_size: Number of characters per chunk.
        overlap: Number of characters to overlap between chunks.

    Returns:
        List of text chunks.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:  # skip empty chunks
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def ingest():
    """Main ingestion function. Reads PDFs + TXT files and stores in ChromaDB."""

    print("=== Legal Corpus Ingestion ===\n")
    print(f"Corpus directory : {CORPUS_DIR}")
    print(f"ChromaDB directory: {CHROMA_DIR}\n")

    os.makedirs(CHROMA_DIR, exist_ok=True)

    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # Delete existing collection to start fresh (idempotent re-run)
    try:
        client.delete_collection(name="legal_corpus")
        print("Deleted existing 'legal_corpus' collection for a fresh rebuild.\n")
    except Exception:
        pass

    collection = client.create_collection(name="legal_corpus")

    documents = []
    metadatas = []
    ids = []
    doc_id = 0

    # --- Process PDF files ---
    pdf_files = glob.glob(os.path.join(CORPUS_DIR, "*.pdf"))
    print(f"Found {len(pdf_files)} PDF file(s)")

    for file_path in pdf_files:
        file_name = os.path.basename(file_path)
        print(f"  Processing: {file_name}")

        text = extract_text_from_pdf(file_path)
        if not text.strip():
            print(f"    WARNING: No text extracted from {file_name}")
            continue

        chunks = chunk_text(text, chunk_size=600, overlap=100)
        print(f"    -> {len(chunks)} chunks")

        for chunk in chunks:
            documents.append(chunk)
            metadatas.append({
                "source_doc": file_name,
                "article_number": "See chunk text",
            })
            ids.append(f"doc_{doc_id}")
            doc_id += 1

    # --- Process TXT files ---
    txt_files = glob.glob(os.path.join(CORPUS_DIR, "*.txt"))
    if txt_files:
        print(f"\nFound {len(txt_files)} TXT file(s)")
        for file_path in txt_files:
            file_name = os.path.basename(file_path)
            print(f"  Processing: {file_name}")

            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    documents.append(line)
                    metadatas.append({
                        "source_doc": file_name,
                        "article_number": "Unknown",
                    })
                    ids.append(f"doc_{doc_id}")
                    doc_id += 1

    # --- Store in ChromaDB ---
    if not documents:
        print(f"\nERROR: No documents found in {CORPUS_DIR}")
        print("Please add the legal corpus PDFs to that folder and re-run.")
        return

    print(f"\nAdding {len(documents)} total chunks to ChromaDB...")

    # ChromaDB has a batch size limit — add in batches of 5000
    batch_size = 5000
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i : i + batch_size]
        batch_meta = metadatas[i : i + batch_size]
        batch_ids = ids[i : i + batch_size]
        collection.add(documents=batch_docs, metadatas=batch_meta, ids=batch_ids)
        print(f"  Added batch {i // batch_size + 1} ({len(batch_docs)} chunks)")

    print("\nIngestion complete!\n")

    # --- Verify with a sample query ---
    print("--- Verification Query: 'unpaid wages' ---")
    results = collection.query(
        query_texts=["employer has not paid salary for 3 months"],
        n_results=3,
    )
    if results and results.get("documents"):
        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i]
            print(f"  Match {i+1} [{meta['source_doc']}]: {doc[:120]}...")
    else:
        print("  No results returned — check that PDFs were extracted correctly.")
    print()


if __name__ == "__main__":
    ingest()
