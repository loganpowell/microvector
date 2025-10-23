"""
Takes a list of chunks and returns a list of embeddings.
"""

import logging
from typing import Union, Optional, cast
from pathlib import Path

import numpy as np
from numpy.typing import NDArray
from sentence_transformers import SentenceTransformer

from microvector.utils import EMBEDDING_MODEL, get_local_model_path

# Use concrete float32 type instead of generic floating[Any] for better type checking
FloatArray = NDArray[np.float32]

# Get logger - let the library consumer configure logging
logger = logging.getLogger(__name__)


# Module-level cache for model instances to avoid re-initialization
# This prevents reloading the model from disk on every function call within the same process
_model_cache: dict[tuple[str, str], SentenceTransformer] = {}


def get_embeddings(
    chunks: Union[list[str], list[dict[str, str]], str],
    key: Optional[str] = None,
    model: str = EMBEDDING_MODEL,
    cache_folder: str = "./.cached_models",
) -> list[FloatArray]:
    logger.debug("Starting get_embeddings function.")
    logger.debug(f"Input chunks type: {type(chunks)}, key: {key}")

    # Use cached model instance if available (for performance within same process)
    # This is the primary optimization - avoiding re-initialization of SentenceTransformer
    cache_key = (model, cache_folder)
    if cache_key in _model_cache:
        logger.debug(f"Using in-memory cached model instance for {model}")
        embedding_model = _model_cache[cache_key]
    else:
        # Check if model exists locally to support offline mode
        local_model_path = get_local_model_path(model, cache_folder)

        if local_model_path:
            # Load from local path (offline mode)
            logger.info(f"Loading model from local path: {local_model_path}")
            embedding_model = SentenceTransformer(
                str(local_model_path),
                trust_remote_code=True,
                model_kwargs={"use_safetensors": True},
            )
        else:
            # Download from HuggingFace Hub (requires internet)
            logger.info(f"Downloading model from HuggingFace: {model}")
            embedding_model = SentenceTransformer(
                model,
                trust_remote_code=True,
                cache_folder=cache_folder,
                model_kwargs={"use_safetensors": True},
            )

        # Cache the loaded instance for subsequent calls in this process
        _model_cache[cache_key] = embedding_model
    # log out the first 5 chunks
    if isinstance(chunks, list):
        # logger.debug(f"First 2 chunks: {json.dumps(chunks[:2], indent=2)}")
        logger.debug(f"Chunk: {len(chunks)}")
    # clean out any of the chunks that don't have the target key
    if (
        isinstance(chunks, list)
        and len(chunks) > 0
        and isinstance(chunks[0], dict)
        and key is not None
    ):
        chunks = [
            chunk
            for chunk in chunks
            if isinstance(chunk, dict) and key in chunk and chunk.get(key) is not None
        ]
        logger.debug(f"Filtered chunk count: {len(chunks)}")

    # print(f"model: {model}")
    # print(chunks)
    warning = "Chunks must be a list of strings or a list of dictionaries."
    if isinstance(chunks, list):
        logger.debug(f"Processing list of chunks with length: {len(chunks)}")
        if len(chunks) > 0 and isinstance(chunks[0], dict):
            texts: list[str] = []
            if isinstance(key, str):
                if "." in key:
                    key_chain = key.split(".")
                else:
                    key_chain = [key]
                for chunk in chunks:
                    # traverse the dictionary to get the value
                    current_val = chunk
                    for k in key_chain:
                        if isinstance(current_val, dict):
                            current_val = current_val[k]
                        else:
                            raise ValueError(f"text not found in key path at: '{k}'")
                    if isinstance(current_val, str):
                        texts.append(current_val.replace("\n", " "))
                    else:
                        raise ValueError(
                            f"Expected text (string) at key path but got: {current_val} ({type(current_val)})"
                        )
            elif key is None:
                for chunk in chunks:
                    # join the key-value pairs with a comma
                    if isinstance(chunk, dict):
                        text = ", ".join(
                            [f"{key}: {value}" for key, value in chunk.items()]
                        )
                    else:
                        raise ValueError(
                            f"Expected dictionary but got: {chunk} ({type(chunk)})"
                        )
                    texts.append(text)
        elif isinstance(chunks, str) and not key:
            # this is just a request for a query string embedding
            texts = [chunks]
        elif isinstance(chunks[0], str):
            logger.debug("Chunks are a list of strings.")
            texts = chunks  # type: ignore
        else:
            # print(chunks)
            raise ValueError(warning)
    else:
        logger.debug("Chunks are not a list.")
        # print(chunks)
        raise ValueError(warning)

    # Show progress bar only if logging level is DEBUG or lower (more verbose)
    show_progress = logger.isEnabledFor(logging.DEBUG)

    logger.debug(f"Encoding {len(texts)} texts")
    embeddings = embedding_model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=show_progress,
    )

    logger.debug("Completed embeddings generation.")
    # Convert to list for consistency with existing API
    return list(embeddings)


def save_model_for_offline_use(
    model_name: str = EMBEDDING_MODEL,
    cache_folder: str = "./.cached_models",
) -> Path:
    """
    Download and save a model for offline use.

    This function downloads a model from HuggingFace Hub and saves it locally
    in a format that can be loaded without internet connectivity.

    Args:
        model_name: HuggingFace model ID (e.g., 'avsolatorio/GIST-small-Embedding-v0')
        cache_folder: Directory to save the model

    Returns:
        Path to the saved model directory

    Example:
        >>> from microvector.embed import save_model_for_offline_use
        >>> model_path = save_model_for_offline_use()
        >>> print(f"Model saved to: {model_path}")
    """
    cache_path = Path(cache_folder)
    cache_path.mkdir(parents=True, exist_ok=True)

    # Sanitize model name for directory (replace '/' with '--')
    safe_model_name = model_name.replace("/", "--")
    save_path = cache_path / safe_model_name

    logger.info(f"Downloading model '{model_name}' for offline use...")
    model = SentenceTransformer(
        model_name,
        trust_remote_code=True,
        model_kwargs={"use_safetensors": True},
    )

    logger.info(f"Saving model to: {save_path}")
    model.save(str(save_path))

    logger.info(f"Model '{model_name}' successfully saved for offline use")
    return save_path
