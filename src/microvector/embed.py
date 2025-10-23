"""
Takes a list of chunks and returns a list of embeddings.
"""

import logging
from typing import Union, Optional, cast

import numpy as np
from numpy.typing import NDArray
from sentence_transformers import SentenceTransformer  # type: ignore

from microvector.utils import EMBEDDING_MODEL

# Use concrete float32 type instead of generic floating[Any] for better type checking
FloatArray = NDArray[np.float32]

logging.basicConfig(
    format="%(levelname)-1s [%(name)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=logging.INFO,
    force=True,
)

logger = logging.getLogger(__name__)

MAX_BATCH_SIZE = 16


def get_embeddings(
    chunks: Union[list[str], list[dict[str, str]], str],
    key: Optional[str] = None,
    model: str = EMBEDDING_MODEL,
    cache_folder: str = "./.cached_models",
) -> list[FloatArray]:
    logger.debug("Starting get_embeddings function.")
    logger.info(f"Input chunks type: {type(chunks)}, key: {key}")
    logger.debug(f"Loading model: {model}")
    embedding_model = SentenceTransformer(
        model,
        trust_remote_code=True,
        cache_folder=cache_folder,
        model_kwargs={"use_safetensors": True},
    )
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

    embeddings: list[FloatArray] = []

    logger.debug(f"Splitting texts into batches of size {MAX_BATCH_SIZE}.")
    batches = [
        texts[i : i + MAX_BATCH_SIZE] for i in range(0, len(texts), MAX_BATCH_SIZE)
    ]
    embeddings = []

    for batch in batches:
        logger.debug(f"Encoding batch with size: {len(batch)}")
        embeds = embedding_model.encode(batch, normalize_embeddings=True)
        # print(f"embeds: {embeds}")
        embeddings.extend(embeds)
    # print(f"embeds: {embeds}")
    logger.debug("Completed embeddings generation.")
    return embeddings
