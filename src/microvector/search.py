import logging
from typing import Any, List, Dict, Union, Optional
from microvector.cache import vector_cache
from microvector.utils import SimilarityMetrics

logging.basicConfig(
    format="%(levelname)-1s [%(name)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=logging.INFO,
    force=True,
)

logger = logging.getLogger(__name__)


def vector_search(
    term: Union[str, int, float, bool],
    partition: Union[int, str],
    key: str,
    top_k: int = 5,
    collection: Optional[Any] = None,
    cache: bool = False,
    algo: SimilarityMetrics = "cosine",
) -> Optional[List[Dict[str, Any]]]:
    """
    Search a vector store with the provided query.

    Args:
        - term (str) The search term to query the vector store.
        - partition (int | str) The partition of the vector store to query.
        - key (str) The key within the collection that is vectorized
        - top_k (int) The number of top results to return.
        - collection (Any | None) Optional collection to filter the results.

    Examples:
    """
    if not isinstance(term, str):
        term = str(term)
    # if the term is empty, return nono
    if term == "":
        logger.error("Search term is empty")
        return None
    # Perform the query using the vector store
    querier = vector_cache(
        partition=partition,
        key=key,
        collection=collection,
        cache=cache,
        algo=algo,
    )
    if querier is None:
        logger.error(
            "Vector store querier is None for partition '%s' and key '%s'.",
            partition,
            key,
        )
        return None
    results: List[Dict[str, Any]] = querier(term, top_k)
    return results
