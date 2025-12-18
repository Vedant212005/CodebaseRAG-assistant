# build_vector_index.py
import json
import numpy as np
import faiss
import os
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def build_vector_index(session_dir: str):
    chunks_file = os.path.join(session_dir, "code_chunks.json")
    embeddings_file = os.path.join(session_dir, "embeddings.npy")
    metadata_file = os.path.join(session_dir, "metadata.json")
    faiss_file = os.path.join(session_dir, "code_index.faiss")

    chunks = json.load(open(chunks_file))

    texts = [c["text_to_embed"] for c in chunks]

    model = SentenceTransformer(MODEL_NAME)
    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True
    ).astype("float32")

    np.save(embeddings_file, embeddings)

    metadata = [
        {
            "file": c["file"],
            "name": c["name"],
            "kind": c["kind"],
            "class": c.get("class"),
            "docstring": c.get("docstring")
        }
        for c in chunks
    ]

    json.dump(metadata, open(metadata_file, "w"), indent=2)

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, faiss_file)
