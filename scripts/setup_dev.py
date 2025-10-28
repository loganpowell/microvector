#!/usr/bin/env python3
"""
Developer setup verification script.
Run this after `uv sync` to verify the environment is set up correctly.
"""


def verify_setup():
    """Verify that all dependencies are installed correctly."""
    print("🔍 Verifying microvector development environment...")

    try:
        import torch

        print(f"✅ PyTorch {torch.__version__} installed")
        print(f"   CUDA available: {torch.cuda.is_available()}")
        print(
            f"   MPS available: {torch.backends.mps.is_available() if hasattr(torch.backends, 'mps') else 'N/A'}"
        )
        print(f"   Device: {torch.device('cpu')}")
    except ImportError:
        print("❌ PyTorch not found")
        return False

    try:
        import transformers

        print(f"✅ Transformers {transformers.__version__} installed")
    except ImportError:
        print("❌ Transformers not found")
        return False

    try:
        import sentence_transformers

        print(f"✅ Sentence Transformers {sentence_transformers.__version__} installed")
    except ImportError:
        print("❌ Sentence Transformers not found")
        return False

    try:
        import numpy as np

        print(f"✅ NumPy {np.__version__} installed")
    except ImportError:
        print("❌ NumPy not found")
        return False

    print("\n✅ All dependencies verified! Your development environment is ready.")
    print("\n📝 To get started:")
    print("   - Import microvector: from microvector.store import Store")
    print("   - Run tests: uv run pytest")
    print("   - Type check: uv run pyright")

    return True


if __name__ == "__main__":
    verify_setup()
