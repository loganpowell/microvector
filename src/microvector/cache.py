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
)
from microvector.store import Store

# Use concrete float32 type instead of generic floating[Any] for better type checking
FloatArray = NDArray[np.float32]

logging.basicConfig(
    format="%(levelname)-1s [%(name)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=logging.INFO,
    force=True,
)

logger = logging.getLogger(__name__)


def get_embeddings_customized(
    key: str,
    model: str = EMBEDDING_MODEL,
    cache_folder: str = "./.cached_models",
) -> Callable[[Any], list[FloatArray]]:
    """
    Just a model passthrough for testing purposes.
    """
    return lambda docs: get_embeddings(
        docs, key=key, model=model, cache_folder=cache_folder
    )


def vector_cache(
    partition: Union[int, str],
    key: str,
    collection: Optional[list[Any]] = None,
    cache: bool = True,
    model: str = EMBEDDING_MODEL,
    algo: SimilarityMetrics = "cosine",
    cache_vectors: str = "./.vector_cache",
    cache_models: str = "./.cached_models",
) -> Callable[[str, int], list[dict[str, Any]]]:
    """
    Wraps multiple cached vector stores with partitioned access
    """
    # Load the vector store for the specified partition
    logger.info("Looking for partition: %s", partition)
    logger.info("Vectorizing for key: %s", key)

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
            db = Store(
                formatted_collection,
                key=key,
                embedding_function=get_embeddings_customized(
                    key=key, model=model, cache_folder=cache_models
                ),
                algo=algo,
            )
            db.save(str(path))
            logger.info("Collection saved to %s", path)
        else:
            logger.info("Loading cached vector store (%s) from %s...", partition, path)
            db = Store(
                key=key,
                embedding_function=get_embeddings_customized(
                    key=key, model=model, cache_folder=cache_models
                ),
                algo=algo,
            )
            db.load(str(path))
    else:
        db = Store(
            formatted_collection,
            key=key,
            embedding_function=get_embeddings_customized(
                key=key, model=model, cache_folder=cache_models
            ),
            algo=algo,
        )

    def query(term: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Query the vector store with the provided query
        """
        # Perform the query using the vector store
        logger.info("Querying vector store for term: '%s' with top_k=%d", term, top_k)
        results = db.query(term, top_k=top_k)
        return results

    return query  # Return the query function instead of yielding it


# test_coll = [
#     {"header": "Another header", "body": "UAE"},
#     {"header": "Third header", "body": "United Kingdom"},
#     {"header": "Fourth header", "body": "United Arab Emirates"},
#     {"header": "Some header", "body": "United State of America"},
#     {"header": "Fifth header", "body": "Patriot"},
# ]

# querier = vector_cache(partition=2, key="body", collection=test_coll)
# results = querier("USA", top_k=5)

# print(f"results: {json.dumps(results, indent=2)}")
