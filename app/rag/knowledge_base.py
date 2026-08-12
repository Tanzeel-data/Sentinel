import chromadb

from app.embeddings.embedder import SentinelEmbedder


COLLECTION_NAME = "sentinel_knowledge"


class SentinelKnowledgeBase:
    """Local ChromaDB knowledge base for Sentinel."""

    def __init__(self):
        self.embedder = SentinelEmbedder()

        self.client = chromadb.PersistentClient(
            path="./chroma_db"
        )

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def add_documents(self, documents):
        """Add knowledge documents to ChromaDB."""

        if not documents:
            return 0

        ids = [
            f"doc_{self.collection.count() + i}"
            for i in range(len(documents))
        ]

        embeddings = self.embedder.embed_texts(documents)

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings.tolist(),
        )

        return len(documents)

    def search(self, query, top_k=3):
        """Retrieve the most relevant knowledge documents."""

        if not query.strip():
            return []

        query_embedding = self.embedder.embed_query(query)

        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
        )

        documents = results.get("documents", [[]])[0]
        distances = results.get("distances", [[]])[0]

        return [
            {
                "document": document,
                "distance": distance,
            }
            for document, distance in zip(
                documents,
                distances,
            )
        ]

    def count(self):
        """Return the number of stored documents."""

        return self.collection.count()