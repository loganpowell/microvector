"""
Microvector: A simple local vector database.

Main exports:
- Client: Primary interface for vector storage and search
- PartitionStore: Represents a cached vector store partition
- EMBEDDING_MODEL: Default embedding model constant
"""

from microvector.main import Client
from microvector.partition import PartitionStore
from microvector.utils import EMBEDDING_MODEL

__all__ = ["Client", "PartitionStore", "EMBEDDING_MODEL"]
