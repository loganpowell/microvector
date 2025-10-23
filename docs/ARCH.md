# End Use

```py

from microvector import Client

mv_client = Client(
    cache_models="path/to/your/model_caching/directory",
    cache_vectors="path/to/your/vector_caching/directory",
    embedding_model="your-hf-embedding-model-name", # defaults to "sentence-transformers/all-MiniLM-L6-v2"
)

# just load data into vector store
results = mv_client.save(
    partition_name="partition_1",
    collection=[ # optional, only needed if adding new data
        {"text": "sample text 1", "metadata": {"source": "source1"}},
        {"text": "sample text 2", "metadata": {"source": "source2"}},
        ...
    ],
)

# search existing data in vector store
results = mv_client.search(
    term="hello world",
    partition_name="partition_1",
    key="text",
    top_k=5,
    algo="cosine",
)

# create and search freshly minted vector store
results = mv_client.search(
    term="hello world",
    partition_name="partition_1",
    key="text",
    top_k=5,
    collection=[ # optional, only needed if adding new data
        {"text": "sample text 1", "metadata": {"source": "source1"}},
        {"text": "sample text 2", "metadata": {"source": "source2"}},
        ...
    ],
    cache=False, # do not persist changes to disk, if True it will save to disk after creating
    algo="cosine",
)

```
