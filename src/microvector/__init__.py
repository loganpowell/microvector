"""
Microvector: A simple local vector database.

Main exports:
- Client: Primary interface for vector storage and search
- EMBEDDING_MODEL: Default embedding model constant
"""

from microvector.main import Client
from microvector.utils import EMBEDDING_MODEL

__all__ = ["Client", "EMBEDDING_MODEL"]
