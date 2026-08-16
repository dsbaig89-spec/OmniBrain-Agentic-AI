from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
)
from backend.app.services.embedding_service import model
import uuid

client = QdrantClient(host="localhost", port=6333,timeout=60)

COLLECTION_NAME = "omnibrain"


def create_collection():
    collections = client.get_collections().collections
    existing = [c.name for c in collections]

    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=384,
                distance=Distance.COSINE,
            ),
        )


def store_embeddings(chunks, embeddings, metadata=None):
    points = []

    for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):

        payload = {
            "text": chunk
        }

        if metadata:
            payload.update(metadata[index])

        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload=payload
            )
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )


def search_vectors(query: str, limit: int = 5):
    query_embedding = model.encode(query).tolist()

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=limit,
        with_payload=True,
    )

    return results.points