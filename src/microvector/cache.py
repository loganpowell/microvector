import json
import os
import logging
from pathlib import Path
import numpy as np
from typing import Any, Callable, Optional, Union
from numpy.typing import NDArray
from microvector.embed import get_embeddings
from microvector.utils import (
    EMBEDDING_MODEL,
    stringify_nonstring_target_values,
    SimilarityMetrics,
    MODEL_CACHE_DIR,
    VECTOR_CACHE_DIR,
)

from microvector.store import Store

# Use concrete float32 type instead of generic floating[Any] for better type checking
FloatArray = NDArray[np.float32]

# Get logger - let the library consumer configure logging
logger = logging.getLogger(__name__)


def vector_cache(
    partition: Union[int, str],
    key: str,
    collection: Optional[list[Any]] = None,
    cache: bool = True,
    model: str = EMBEDDING_MODEL,
    algo: SimilarityMetrics = "cosine",
    cache_vectors: str = VECTOR_CACHE_DIR,
    cache_models: str = MODEL_CACHE_DIR,
    append: bool = False,
) -> Callable[[str, int], list[dict[str, Any]]]:
    """
    Wraps multiple cached vector stores with partitioned access

    Args:
        - partition (int | str) The partition of the vector store to query.
        - key (str) The key within the collection that is vectorized
        - collection (list[Any] | None) Optional collection to filter the results.
        - cache (bool) Whether to persist the vector store to disk.
        - model (str) HuggingFace embedding model name.
        - algo (SimilarityMetrics) Similarity metric to use.
        - cache_vectors (str) Path to directory for caching vector stores.
        - cache_models (str) Path to directory for caching embedding models.
        - append (bool) If True, adds new vectors to existing cache. If False (default),
            replaces existing cache with new vectors.
    """
    # Load the vector store for the specified partition
    logger.info("Looking for partition: %s", partition)
    logger.info("Vectorizing for key: %s", key)

    embed = lambda docs: get_embeddings(
        docs, key=key, model=model, cache_folder=cache_models
    )

    # Helper to create Store instances with consistent parameters
    def create_store(data: Optional[list[Any]] = None) -> Store:
        return Store(
            data,
            key=key,
            embedding_function=embed,
            algo=algo,
        )

    # lowercase snake_case partition e.g.: Applies To Selected Jurisdiction Only
    partition = str(partition).lower().replace(" ", "_")
    formatted_collection: Optional[list[Any]] = None
    if collection is not None:
        formatted_result = stringify_nonstring_target_values(collection, key)
        if isinstance(formatted_result, list):
            formatted_collection = formatted_result

    # check if the file exists
    if cache:
        path = Path(cache_vectors, f"{partition}.pickle.gz")
        if not os.path.exists(path):
            logger.debug(
                "Storing vectors for collection: %s",
                json.dumps(collection, indent=2)[0:333],
            )
            logger.info("Vector store cache file not found: %s. Creating...", path)
            # create the directory if it doesn't exist
            os.makedirs(os.path.dirname(path), exist_ok=True)
            logger.info("Loading collection. Please wait...")
            # Load the collection
            db = create_store(formatted_collection)
            db.save(str(path))
            logger.info("Collection saved to %s", path)
        else:
            logger.info("Loading cached vector store (%s) from %s...", partition, path)
            db = create_store()
            db.load(str(path))

            # If append mode and we have a new collection, add it to the existing store
            if append and formatted_collection:
                logger.info(
                    "Appending %d documents to existing vector store",
                    len(formatted_collection),
                )
                db.add_collection(formatted_collection)
                db.save(str(path))
                logger.info("Updated collection saved to %s", path)
            # If not append mode and we have a new collection, replace the existing store
            elif not append and formatted_collection:
                logger.info(
                    "Replacing existing vector store with %d new documents",
                    len(formatted_collection),
                )
                db = create_store(formatted_collection)
                db.save(str(path))
                logger.info("Replaced collection saved to %s", path)
    else:
        # cache=False: Check if we should load existing cache and append temporarily
        path = Path(cache_vectors, f"{partition}.pickle.gz")
        if append and os.path.exists(path):
            # Load existing cache but don't persist changes
            logger.info(
                "Loading cached vector store (%s) for temporary append (not persisted)...",
                partition,
            )
            db = create_store()
            db.load(str(path))

            # Append new collection to the loaded store (in memory only)
            if formatted_collection:
                logger.info(
                    "Temporarily appending %d documents to existing vector store (not persisted)",
                    len(formatted_collection),
                )
                db.add_collection(formatted_collection)
        else:
            # No existing cache or append=False: create new temporary store
            db = create_store(formatted_collection)

    def query(term: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Query the vector store with the provided query
        """
        # Perform the query using the vector store
        logger.info("Querying vector store for term: '%s' with top_k=%d", term, top_k)
        results = db.query(term, top_k=top_k)
        return results

    return query  # Return the query function instead of yielding it
