import random
from typing import Tuple

import numpy as np
from numpy.typing import NDArray

# Use concrete float32 type instead of generic floating[Any] for better type checking
FloatArray = NDArray[np.float32]


def get_norm_vector(vector: FloatArray) -> FloatArray:
    if len(vector.shape) == 1:
        return (vector / np.linalg.norm(vector)).astype(np.float32)
    else:
        return (vector / np.linalg.norm(vector, axis=1)[:, np.newaxis]).astype(
            np.float32
        )


def dot_product(
    vectors: FloatArray, query_vector: FloatArray, top_k: int = 5
) -> Tuple[NDArray[np.intp], FloatArray]:
    similarities = np.dot(vectors, query_vector.T).astype(np.float32)
    top_indices = np.argsort(similarities, axis=0)[-top_k:][::-1]
    return top_indices.flatten(), similarities[top_indices].flatten()


def cosine_similarity(
    vectors: FloatArray, query_vector: FloatArray, top_k: int = 5
) -> Tuple[NDArray[np.intp], FloatArray]:
    norm_vectors = get_norm_vector(vectors)
    norm_query_vector = get_norm_vector(query_vector)
    similarities = np.dot(norm_vectors, norm_query_vector.T).astype(np.float32)
    top_indices = np.argsort(similarities, axis=0)[-top_k:][::-1]
    return top_indices.flatten(), similarities[top_indices].flatten()


def euclidean_metric(
    vectors: FloatArray,
    query_vector: FloatArray,
    top_k: int = 5,
    get_similarity_score: bool = True,
) -> Tuple[NDArray[np.intp], FloatArray]:
    similarities = np.linalg.norm(vectors - query_vector, axis=1).astype(np.float32)
    if get_similarity_score:
        similarities = (1 / (1 + similarities)).astype(np.float32)
    top_indices = np.argsort(similarities, axis=0)[-top_k:][::-1]
    return top_indices.flatten(), similarities[top_indices].flatten()


def derridaean_similarity(
    vectors: FloatArray, query_vector: FloatArray, top_k: int = 5
) -> Tuple[NDArray[np.intp], FloatArray]:
    def random_change(value: float) -> float:
        return value + random.uniform(-0.2, 0.2)

    # Compute all cosine similarities (not top-k yet)
    norm_vectors = get_norm_vector(vectors)
    norm_query_vector = get_norm_vector(query_vector)
    similarities = np.dot(norm_vectors, norm_query_vector.T).astype(np.float32)
    derrida_similarities: FloatArray = np.vectorize(random_change)(similarities).astype(
        np.float32
    )
    top_indices = np.argsort(derrida_similarities, axis=0)[-top_k:][::-1]
    return top_indices.flatten(), derrida_similarities[top_indices].flatten()
