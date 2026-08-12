from app.database.query import get_recent_logs
from app.embeddings.embedder import SentinelEmbedder


def log_to_text(log):
    """Convert a database log record into searchable text."""

    log_id, server_id, timestamp, level, message, service = log

    return (
        f"Server: {server_id}\n"
        f"Service: {service}\n"
        f"Level: {level}\n"
        f"Timestamp: {timestamp}\n"
        f"Message: {message}"
    )


if __name__ == "__main__":
    logs = get_recent_logs(10)

    texts = [log_to_text(log) for log in logs]

    embedder = SentinelEmbedder()

    embeddings = embedder.embed_texts(texts)

    print("\nEmbedding test successful")
    print("Documents:", len(texts))
    print("Embedding dimension:", embeddings.shape[1])
    print("First vector length:", len(embeddings[0]))