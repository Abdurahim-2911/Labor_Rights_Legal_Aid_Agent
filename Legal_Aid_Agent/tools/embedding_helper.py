"""
Gemini Embedding Function for ChromaDB

Provides a custom embedding function using the google-genai SDK
to avoid downloading large ONNX models locally and ensure compatibility
with the Gemini family of models.
"""

import os
from dotenv import load_dotenv
from chromadb import EmbeddingFunction, Documents, Embeddings
from google import genai


class GeminiEmbeddingFunction(EmbeddingFunction):
    """Custom embedding function utilizing Gemini's embedding API."""

    def __init__(self, model_name: str = "gemini-embedding-001"):
        # Load environment variables (.env has GOOGLE_API_KEY)
        load_dotenv()
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "API Key not found. Please set GEMINI_API_KEY or GOOGLE_API_KEY in your environment or .env file."
            )
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def __call__(self, input: Documents) -> Embeddings:
        """Embeds a list of documents (strings) using Gemini."""
        if not input:
            return []

        embeddings = []
        # Gemini API supports batching; we chunk input list into batches of 100 (which is the server limit).
        batch_size = 100
        import time
        for i in range(0, len(input), batch_size):
            batch = input[i : i + batch_size]
            
            retries = 5
            delay = 2
            for attempt in range(retries):
                try:
                    response = self.client.models.embed_content(
                        model=self.model_name,
                        contents=batch
                    )
                    if response and response.embeddings:
                        embeddings.extend([emb.values for emb in response.embeddings])
                        # Introduce a small sleep of 1.5 seconds between successful batches
                        # to stay under the free tier rate limits (RPM).
                        time.sleep(1.5)
                        break
                    else:
                        raise RuntimeError("Received empty response from Gemini Embedding API.")
                except Exception as e:
                    # Check for rate limits (HTTP 429 / RESOURCE_EXHAUSTED)
                    is_rate_limit = "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e)
                    if is_rate_limit and attempt < retries - 1:
                        time.sleep(delay)
                        delay *= 2
                    else:
                        print(f"Error calling Gemini Embedding API: {e}")
                        raise e

        return embeddings
