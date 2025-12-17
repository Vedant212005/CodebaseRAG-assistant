# utils/repo_utils.py
import os
import shutil
from git import Repo

def clone_github_repo(repo_url: str, base_dir: str) -> str:
    """
    Clone a GitHub repository into base_dir/repo.
    base_dir MUST be a session-specific directory.
    """

    repo_path = os.path.join(base_dir, "repo")

    # Ensure clean repo directory for this session
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)

    os.makedirs(base_dir, exist_ok=True)

    Repo.clone_from(repo_url, repo_path)

    print(f"[INFO] Repository cloned to {repo_path}")
    return repo_path
