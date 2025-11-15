import json
import numpy as np
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
import faiss
import os

# ---------- CONFIG ----------
CHUNKS_FILE = "code_chunks.json"
EMBEDDINGS_FILE = "embeddings.npy"
METADATA_FILE = "metadata.json"
FAISS_FILE = "code_index.faiss"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# ---------- STEP 1: Load parsed chunks ----------
with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
    chunks = json.load(f)

print(f"Loaded {len(chunks)} code chunks from {CHUNKS_FILE}")

# ---------- STEP 2: Prepare texts for embedding ----------
texts = [c["text_to_embed"] for c in chunks]

# ---------- STEP 3: Load embedding model ----------
print(f"Loading embedding model: {MODEL_NAME}")
model = SentenceTransformer(MODEL_NAME)

# ---------- STEP 4: Generate embeddings ----------
print("Generating embeddings...")
embeddings = model.encode(
    texts,
    batch_size=32,
    show_progress_bar=True,
    convert_to_numpy=True,
    normalize_embeddings=True  # ensures cosine ≈ inner product
).astype("float32")

print(f"Generated embeddings of shape {embeddings.shape}")

# ---------- STEP 5: Save embeddings ----------
np.save(EMBEDDINGS_FILE, embeddings)
print(f"Saved embeddings - {EMBEDDINGS_FILE}")

# ---------- STEP 6: Create metadata ----------
metadata = [
    {
        "id": i,
        "file": c["file"],
        "name": c["name"],
        "kind": c["kind"],
        "class": c.get("class"),
        "lineno_start": c.get("lineno_start"),
        "lineno_end": c.get("lineno_end"),
        "docstring": c.get("docstring"),
        "text_to_embed": c.get("text_to_embed")
    }
    for i, c in enumerate(chunks)
]

with open(METADATA_FILE, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

print(f"Saved metadata - {METADATA_FILE}")

# ---------- STEP 7: Build FAISS index ----------
dim = embeddings.shape[1]
index = faiss.IndexFlatIP(dim)  # cosine similarity (via inner product)
index.add(embeddings)

faiss.write_index(index, FAISS_FILE)
print(f"Saved FAISS index - {FAISS_FILE}")
print(f"Indexed {index.ntotal} code chunks total.")
