import logging
from typing import Any, Union, Literal, Optional
from pathlib import Path
from sentence_transformers import SentenceTransformer

# Get logger - let the library consumer configure logging
logger = logging.getLogger(__name__)

# Default embedding model (supports safetensors for security)
EMBEDDING_MODEL = "avsolatorio/GIST-small-Embedding-v0"

SimilarityMetrics = Literal["dot", "cosine", "euclidean", "derrida"]


def stringify_nonstring_target_values(collection: list | dict, key):
    """
    Recursively convert the value of any key in the dictionary to a string.

    Example:
    result = stringify_nonstring_target_values([
        {"header": "Another header", "is_good": False, "deep": {"deep_key": 1}},
        {"header": "Third header", "is_good": True, "deep": {"deep_key": 2}},
    ]

    print(result)
    # [
    #     {"header": "Another header", "is_good": "False", "deep": {"deep_key": "1"}},
    #     {"header": "Third header", "is_good": "True", "deep": {"deep_key": "2"}},
    # ]
    """
    # leaf node
    if isinstance(collection, (str, int, float, bool)) or not collection:
        return collection
    elif isinstance(collection, dict):
        # check if the key is in the dictionary
        if key in collection and isinstance(collection[key], (int, float, bool)):
            # convert the value to a string
            collection[key] = str(collection[key])
        # recursively call the function for each value in the dictionary
        else:
            for k, v in collection.items():
                collection[k] = stringify_nonstring_target_values(v, key)
    elif isinstance(collection, list):
        # recursively call the function for each item in the list
        for i in range(len(collection)):
            collection[i] = stringify_nonstring_target_values(collection[i], key)
    return collection


def get_local_model_path(model_name: str, cache_folder: str) -> Optional[Path]:
    """
    Check if model exists locally in cache_folder.

    Returns the local path if found, None otherwise.
    SentenceTransformer saves models in format: cache_folder/model_name
    where model_name can be the HuggingFace ID (e.g., 'bert-base-nli-stsb-mean-tokens')
    or a sanitized version with '--' replacing '/' (e.g., 'avsolatorio--GIST-small-Embedding-v0')
    """
    cache_path = Path(cache_folder)
    logger.debug(f"Checking for local model '{model_name}' in {cache_path}")

    # Try direct model name as path (for models saved with model.save())
    direct_path = cache_path / model_name
    logger.debug(f"Checking direct path: {direct_path}")
    if direct_path.exists() and (direct_path / "config.json").exists():
        logger.debug(f"Found local model at: {direct_path}")
        return direct_path

    # Try sanitized name (replace '/' with '--')
    sanitized_name = model_name.replace("/", "--")
    sanitized_path = cache_path / sanitized_name
    logger.debug(f"Checking sanitized path: {sanitized_path}")
    if sanitized_path.exists() and (sanitized_path / "config.json").exists():
        logger.debug(f"Found local model at: {sanitized_path}")
        return sanitized_path

    # Try HuggingFace cache format: models--org--model_name
    hf_cache_name = f"models--{model_name.replace('/', '--')}"
    hf_path = cache_path / hf_cache_name
    logger.debug(f"Checking HF cache path: {hf_path}")
    if hf_path.exists():
        # Check for snapshots directory (HuggingFace cache structure)
        snapshots_dir = hf_path / "snapshots"
        if snapshots_dir.exists():
            # Get the latest snapshot
            snapshots = sorted(
                snapshots_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True
            )
            if snapshots:
                logger.debug(f"Found HuggingFace cached model at: {snapshots[0]}")
                return snapshots[0]

    logger.debug(f"No local model found for '{model_name}' in {cache_folder}")
    return None
