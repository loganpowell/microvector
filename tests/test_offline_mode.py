"""
Tests for offline model loading functionality.
"""

import tempfile
from pathlib import Path

import pytest

from microvector.embed import get_embeddings, save_model_for_offline_use
from microvector.utils import EMBEDDING_MODEL


@pytest.fixture(scope="module")
def offline_model_cache(tmp_path_factory):
    """
    Shared fixture that saves the model once for all offline tests.
    Uses module scope so the model is saved only once per test run.
    """
    cache_dir = tmp_path_factory.mktemp("offline_model_cache")

    # Save model once for all tests in this module
    saved_path = save_model_for_offline_use(
        model_name=EMBEDDING_MODEL, cache_folder=str(cache_dir)
    )

    yield str(cache_dir), saved_path

    # Cleanup happens automatically with tmp_path_factory


class TestOfflineMode:
    """Tests for offline model caching and loading."""

    def test_save_model_for_offline_use(self, offline_model_cache):
        """Test that the model was saved correctly."""
        cache_dir, saved_path = offline_model_cache

        # Verify the saved directory exists
        assert saved_path.exists(), f"Model directory not found: {saved_path}"
        assert (saved_path / "config.json").exists(), "config.json not found"

        # Verify key model files exist
        assert (
            saved_path / "model.safetensors"
        ).exists(), "model.safetensors not found"
        assert (saved_path / "tokenizer.json").exists(), "tokenizer.json not found"
        assert (saved_path / "config_sentence_transformers.json").exists()

    def test_load_model_from_offline_cache(self, offline_model_cache):
        """Test loading a model from offline cache."""
        cache_dir, saved_path = offline_model_cache
        assert saved_path.exists()

        # Load the model (should use local version)
        embeddings = get_embeddings(
            chunks=["test document 1", "test document 2"], cache_folder=cache_dir
        )

        # Verify embeddings
        assert len(embeddings) == 2, "Should have 2 embeddings"
        assert len(embeddings[0]) > 0, "Embeddings should not be empty"
        assert all(
            len(emb) == len(embeddings[0]) for emb in embeddings
        ), "All embeddings should have same dimension"

    def test_offline_mode_complete_workflow(self, offline_model_cache):
        """Test complete offline workflow: verify save then load."""
        cache_dir, saved_path = offline_model_cache

        # Verify save
        assert saved_path.exists(), f"Model directory not found: {saved_path}"
        assert (saved_path / "config.json").exists(), "config.json not found"

        # Load model from offline cache
        embeddings = get_embeddings(
            chunks=["test document 1", "test document 2"], cache_folder=cache_dir
        )

        # Verify embeddings
        assert len(embeddings) == 2, "Should have 2 embeddings"
        assert len(embeddings[0]) > 0, "Embeddings should not be empty"

        # Use again to verify caching works
        embeddings2 = get_embeddings(
            chunks=["another test document"], cache_folder=cache_dir
        )

        assert len(embeddings2) == 1, "Should have 1 embedding"
        assert len(embeddings2[0]) == len(
            embeddings[0]
        ), "Embedding dimensions should match"
