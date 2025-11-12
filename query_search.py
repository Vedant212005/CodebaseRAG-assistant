import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# ==== CONFIG ====
FAISS_FILE = "code_index.faiss"
METADATA_FILE = "metadata.json"
CHUNKS_FILE = "chunks.json"   # file containing actual code chunks
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
TOP_K = 5  # number of top results

# ==== GEMINI SETUP ====
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel("gemini-2.5-flash")

# ==== LOAD MODELS AND DATA ====
print("🔄 Loading FAISS index and metadata...")
index = faiss.read_index(FAISS_FILE)
metadata = json.load(open(METADATA_FILE, "r", encoding="utf-8"))
chunks_data = json.load(open(CHUNKS_FILE, "r", encoding="utf-8"))
embed_model = SentenceTransformer(MODEL_NAME)
print("✅ All data loaded successfully.\n")

# ==== USER QUERY ====
query = input("Ask something about the code: ")
query_emb = embed_model.encode([query], normalize_embeddings=True).astype("float32")

# ==== FAISS SEARCH ====
D, I = index.search(query_emb, TOP_K)

# ==== DISPLAY RESULTS ====
print("\n🔍 Top Matches:\n")
selected_chunks = []

for rank, idx in enumerate(I[0]):
    m = metadata[idx]
    print(f"🔹 Rank {rank+1} | File: {m['file']} | Name: {m['name']}")
    print(f"Docstring: {m['docstring']}\n")

    # Find the actual code chunk from chunks.json
    for c in chunks_data:
        if c["file"] == m["file"] and c["name"] == m["name"]:
            selected_chunks.append(c["code"])
            break

# ==== CREATE CONTEXT FOR GEMINI ====
if selected_chunks:
    print("🧩 Constructing context for Gemini...")
    context = "\n\n".join(selected_chunks)

    prompt_template = f"""
You are an expert code assistant.

Here is the relevant code context retrieved based on the user’s query:

{context}

User Query: {query}

Please analyze the code and answer the question clearly.
Focus only on what’s available in the provided context.
If needed, explain how the code works or what it does.
"""

    print("\n=== Sending Prompt to Gemini ===\n")

    # ==== SEND TO GEMINI ====
    response = model.generate_content(prompt_template)

    print("\n💬 Gemini Response:\n")
    print(response.text)
else:
    print("⚠️ No matching code chunks found for the retrieved results.")
