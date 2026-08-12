from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"


class SentinelEmbedder:
    """Local embedding model for Sentinel telemetry."""

    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)

    def embed_texts(self, texts):
        """Generate embeddings for multiple texts."""
        return self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

    def embed_query(self, query):
        """Generate an embedding for a user query."""
        return self.model.encode(
            query,
            normalize_embeddings=True,
        )

    @property
    def dimension(self):
        return self.model.get_embedding_dimension()