from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from utils.repo_utils import clone_github_repo
from utils.runner import run_ingest, run_build_vector

import faiss
import json
import os
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from dotenv import load_dotenv

# =====================
# ENV & CONFIG
# =====================
load_dotenv()

FAISS_FILE = "code_index.faiss"
METADATA_FILE = "metadata.json"
CHUNKS_FILE = "code_chunks.json"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
TOP_K = 5

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY missing")

genai.configure(api_key=GEMINI_API_KEY)

# =====================
# APP INIT
# =====================
app = FastAPI(title="RAG CodeBase API")

# =====================
# LOAD MODELS (ONCE)
# =====================
embed_model = SentenceTransformer(MODEL_NAME)
gemini_model = genai.GenerativeModel("gemini-2.5-flash")

index = None
metadata = None
chunks_data = None


# =====================
# REQUEST SCHEMAS
# =====================
class RepoRequest(BaseModel):
    repo_url: str

class QueryRequest(BaseModel):
    query: str


# =====================
# HELPERS
# =====================
def load_vector_store():
    global index, metadata, chunks_data

    if not os.path.exists(FAISS_FILE):
        raise RuntimeError("FAISS index not found. Process a repo first.")

    index = faiss.read_index(FAISS_FILE)
    metadata = json.load(open(METADATA_FILE, "r", encoding="utf-8"))
    chunks_data = json.load(open(CHUNKS_FILE, "r", encoding="utf-8"))


def build_context(query: str) -> str:
    query_emb = embed_model.encode([query], normalize_embeddings=True).astype("float32")
    D, I = index.search(query_emb, TOP_K)

    selected_chunks = []
    for idx in I[0]:
        m = metadata[idx]
        for c in chunks_data:
            if c["file"] == m["file"] and c["name"] == m["name"]:
                selected_chunks.append(c["code"])
                break

    if not selected_chunks:
        return ""

    return "\n\n".join(selected_chunks)


def call_gemini(context: str, query: str) -> str:
    prompt = f"""
You are an expert code assistant.

Here is the relevant code context retrieved from the repository:

{context}

User Question:
{query}

Answer clearly using ONLY the given code context.
"""

    response = gemini_model.generate_content(prompt)
    return response.text


# =====================
# ROUTES
# =====================
@app.post("/process_repo")
def process_repo(request: RepoRequest):
    """
    Clone repo and build FAISS index.
    """
    try:
        repo_path = clone_github_repo(request.repo_url)
        run_ingest(repo_path)
        run_build_vector()

        load_vector_store()  # reload index after processing

        return {"message": "Repository processed successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query")
def query_codebase(request: QueryRequest):
    """
    Query the processed repository using FAISS + Gemini.
    """
    try:
        if index is None:
            load_vector_store()

        context = build_context(request.query)

        if not context:
            return {"response": "No relevant code found for this query."}

        answer = call_gemini(context, request.query)

        return {"response": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
