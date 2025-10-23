import gzip
import pickle
from pathlib import Path
from typing import Any, Callable, Optional, Union
from microvector.utils import SimilarityMetrics

import numpy as np
from numpy.typing import NDArray

# Use concrete float32 type instead of generic floating[Any] for better type checking
FloatArray = NDArray[np.float32]

# import openai
from microvector.algos import (
    cosine_similarity,
    derridaean_similarity,
    dot_product,
    euclidean_metric,
)
from microvector.embed import get_embeddings


def unpack_results(results: list[tuple[Any, float]]) -> list[dict[str, Any]]:
    """
    [({'header': 'some header', 'body': 'some body'}, np.float32(0.08397958)), ...] ⤵
    [{'header': 'some header', 'body': 'some body', 'similarity_score': 0.08397958 }, ...]

    Or for string documents:
    [('some text', np.float32(0.95)), ...] ⤵
    [{'document': 'some text', 'similarity_score': 0.95}, ...]
    """
    unpacked: list[dict[str, Any]] = []
    for document, similarity in results:
        if isinstance(document, dict):
            unpacked.append({**document, "similarity_score": float(similarity)})
        else:
            unpacked.append(
                {"document": document, "similarity_score": float(similarity)}
            )
    return unpacked


EmbeddingFunction = Callable[[Any], list[FloatArray]]


class Store:
    collection: list[Any]
    vectors: Optional[FloatArray]
    embedding_function: EmbeddingFunction
    algo: SimilarityMetrics  # Can be any of the similarity functions from algos

    def __init__(
        self,
        collection: Optional[list[Any]] = None,
        vectors: Optional[FloatArray] = None,
        key: Optional[str] = None,
        embedding_function: Optional[EmbeddingFunction] = None,
        algo: SimilarityMetrics = "cosine",
    ):
        collection = collection or []
        self.collection = []
        self.vectors = None

        if embedding_function is not None:
            self.embedding_function = embedding_function
        else:
            self.embedding_function = lambda docs: get_embeddings(docs, key=key)

        if vectors is not None:
            self.vectors = vectors
            self.collection = collection
        else:
            self.add_collection(collection)

        if "dot" in algo:
            self.sort = dot_product
        elif "cosine" in algo:
            self.sort = cosine_similarity
        elif "euclidean" in algo:
            self.sort = euclidean_metric
        elif "derrida" in algo:
            self.sort = derridaean_similarity
        else:
            raise ValueError(
                "Similarity metric not supported. \nPlease use one of: 'dot', 'cosine', 'euclidean', 'adams', or 'derrida'."
            )

    def to_dict(self, vectors: bool = False) -> list[dict[str, Any]]:
        if vectors:
            if self.vectors is None:
                return []
            return [
                {"document": document, "vector": vector.tolist(), "index": index}
                for index, (document, vector) in enumerate(
                    zip(self.collection, self.vectors)
                )
            ]
        return [
            {"document": document, "index": index}
            for index, document in enumerate(self.collection)
        ]

    def add(
        self,
        collection: Union[Any, list[Any]],
        vectors: Optional[FloatArray] = None,
    ) -> None:
        if not isinstance(collection, list):
            self.add_document(collection, vectors)
        else:
            self.add_collection(collection, vectors)  # type: ignore

    def add_document(self, document: Any, vector: Optional[FloatArray] = None) -> None:
        resolved_vector: FloatArray = (
            vector if vector is not None else self.embedding_function([document])[0]
        )
        if self.vectors is None:
            self.vectors = np.empty((0, len(resolved_vector)), dtype=np.float32)
        elif len(resolved_vector) != self.vectors.shape[1]:
            raise ValueError("All vectors must have the same length.")
        self.vectors = np.vstack([self.vectors, resolved_vector]).astype(np.float32)
        self.collection.append(document)

    def remove_document(self, index: int) -> None:
        if self.vectors is not None:
            self.vectors = np.delete(self.vectors, index, axis=0)
        self.collection.pop(index)

    def add_collection(
        self, collection: list[Any], vectors: Optional[FloatArray] = None
    ) -> None:
        if not collection:
            return
        resolved_vectors: FloatArray = (
            vectors
            if vectors is not None
            else np.array(self.embedding_function(collection)).astype(np.float32)
        )
        # print(f"Vectors: {vectors}")
        for vector, document in zip(resolved_vectors, collection):
            self.add_document(document, vector)

    def save(self, storage_file: str) -> None:
        # Ensure parent directory exists
        Path(storage_file).parent.mkdir(parents=True, exist_ok=True)

        data = {"vectors": self.vectors, "collection": self.collection}
        if storage_file.endswith(".gz"):
            with gzip.open(storage_file, "wb") as f:
                pickle.dump(data, f)  # type: ignore
        else:
            with open(storage_file, "wb") as f:
                pickle.dump(data, f)

    def load(self, storage_file: str) -> None:
        if storage_file.endswith(".gz"):
            with gzip.open(storage_file, "rb") as f:
                data = pickle.load(f)  # type: ignore
        else:
            with open(storage_file, "rb") as f:
                data = pickle.load(f)
        self.vectors = data["vectors"].astype(np.float32)
        self.collection = data["collection"]
        # print(f"First vector: {self.vectors[0]}")
        # print(f"First document: {self.collection[0]}")

    def query(self, query_text: str, top_k: int = 5) -> list[dict[str, Any]]:
        if self.vectors is None:
            raise ValueError("No vectors available for querying")
        query_vector = self.embedding_function([query_text])[0]
        ranked_results: NDArray[np.intp]
        similarities: FloatArray
        ranked_results, similarities = self.sort(
            self.vectors, query_vector, top_k=top_k
        )
        return unpack_results(
            list(
                zip(
                    [self.collection[index] for index in ranked_results],
                    similarities,
                )
            )
        )
