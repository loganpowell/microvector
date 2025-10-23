# from vector.chunk import chunk_pdf_by_headings
# from microvector.db import (
#     # db,
#     get_embeddings_customized,
# )
# from microvector.store import Store


# from vector.embed import get_embeddings
# from vector.store import Store

# os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

# Load documents from the JSONL file
# chunks = chunk_pdf_by_headings(
#     "assets/tax_assist_in_the_o_series_user_interface_1-2-2025.pdf",
# )

# print(f"First three chunks: {json.dumps(chunks[:3], indent=2)}")

# embeddings = get_embeddings(chunks, key="body", model="Alibaba-NLP/gte-base-en-v1.5")

# models tried:
# "Alibaba-NLP/gte-base-en-v1.5" 😃
# "sentence-transformers/all-MiniLM-L6-v2" 😄
# "jxm/cde-small-v2" 😦
# "BAAI/bge-base-en-v1.5" 😍
# "infgrad/stella-base-en-v2" 😻 <- mighty mouse! (half the size, same power)


# def get_embeddings_customized(
#     docs: list[str] | list[dict[str, str]],
# ):
#     """
#     Just a model passthrough for testing purposes.
#     """
#     return get_embeddings(docs, key="body", model="infgrad/stella-base-en-v2")


# Instantiate HyperDB with the list of documents
# db = Store(chunks, key="body", embedding_function=get_embeddings_customized)

# Or instantiate an empty store to load from pickle file
# db = Store(key="body", embedding_function=get_embeddings_customized)

# Save the HyperDB instance to a file
# db.save("assets/chunk_vector_store.pickle.gz")

# Load the HyperDB instance from the save file
# db.load("assets/chunk_vector_store.pickle.gz")

# Query the HyperDB instance with a text input
# results = db.query("seller's company", top_k=5)

# print(f"results: {json.dumps(results, indent=2)}")


# db = Store(key="body", embedding_function=get_embeddings_customized)

# db.load("assets/chunk_vector_store.pickle.gz")

# Query the HyperDB instance with a text input
# results = db.query("seller's company", top_k=5)

# print(f"results: {json.dumps(results, indent=2)}")
