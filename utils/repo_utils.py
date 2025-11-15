# utils/repo_utils.py
import os
import shutil
from git import Repo

def clone_github_repo(repo_url: str, clone_dir: str = "cloned_repo"):
    """Clones a GitHub repo to a local folder. If folder exists, it deletes and reclones."""
    if os.path.exists(clone_dir):
        shutil.rmtree(clone_dir)
    Repo.clone_from(repo_url, clone_dir)
    print(f"Repository cloned to {clone_dir}")
    return os.path.abspath(clone_dir)
