import os
import json
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance


def upload_json_points_to_qdrant(
    collection_name: str,
    data_dir: str = "data\ready jsons",
    host: str = "localhost",
    port: int = 6333
):
    client = QdrantClient(host=host, port=port)

    sample_file = next(f for f in os.listdir(data_dir) if f.endswith(".json"))
    with open(os.path.join(data_dir, sample_file), "r", encoding="utf-8") as f:
        sample_data = json.load(f)
        vector_dim = len(sample_data["vector"])

    if not client.collection_exists(collection_name):
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_dim, distance=Distance.COSINE)
        )

    points = []
    for filename in os.listdir(data_dir):
        if not filename.endswith(".json"):
            continue

        with open(os.path.join(data_dir, filename), "r", encoding="utf-8") as f:
            data = json.load(f)

        point = PointStruct(
            id=data["id"],
            vector=data["vector"],
            payload={"text": data.get("text", "")}
        )
        points.append(point)

    client.upsert(collection_name=collection_name, points=points)


if __name__ == "__main__":
    upload_json_points_to_qdrant("sigmaRP_large")
