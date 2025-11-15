# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from utils.repo_utils import clone_github_repo
from utils.runner import run_ingest, run_build_vector, run_query_search

app = FastAPI(title="RAG CodeBase API")

class RepoRequest(BaseModel):
    repo_url: str

class QueryRequest(BaseModel):
    query: str


@app.post("/process_repo")
def process_repo(request: RepoRequest):
    """
    1. Clone the given GitHub repo.
    2. Run ingest.py and build_vector.py to generate embeddings and index.
    """
    try:
        repo_path = clone_github_repo(request.repo_url)
        run_ingest(repo_path)
        run_build_vector()
        return {"message": "Repository processed successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query")
def query_codebase(request: QueryRequest):
    """
    Run the query_search.py logic on the existing index and return the response.
    """
    try:
        result = run_query_search(request.query)
        return {"response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
