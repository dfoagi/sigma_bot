from qdrant_client import QdrantClient


def get_qdrant_client(host: str, api_key: str = "") -> QdrantClient:
    return QdrantClient(url=host, api_key=api_key)


def get_relevant_chunks(client: QdrantClient, collection_name: str, question_vector: list, top_k: int=3):
    return client.query_points(
        collection_name=collection_name,
        query=question_vector,
        limit=top_k,
        with_payload=True,
        with_vectors=False
    )
