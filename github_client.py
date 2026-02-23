from typing import Dict, List, Optional, Tuple
from urllib.parse import quote, urlparse

import requests
from fastapi import HTTPException

from constants import MAX_FILE_BYTES, REQUEST_TIMEOUT


class GitHubRepositoryClient:
    def __init__(self, timeout: int = REQUEST_TIMEOUT):
        self.timeout = timeout
        self.headers = {"Accept": "application/vnd.github+json"}

    def parse_url(self, url: str) -> Tuple[str, str]:
        try:
            parsed = urlparse(url)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid GitHub URL") from exc

        if parsed.netloc != "github.com":
            raise HTTPException(status_code=400, detail="Only github.com URLs are supported")

        path_parts = [p for p in parsed.path.strip("/").split("/") if p]
        if len(path_parts) < 2:
            raise HTTPException(status_code=400, detail="GitHub URL must include owner and repo")

        owner = path_parts[0]
        repo = path_parts[1].removesuffix(".git")
        if not owner or not repo:
            raise HTTPException(status_code=400, detail="Invalid GitHub URL format")

        return owner, repo

    def api_get(self, url: str) -> Dict:
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Repository not found")
        if response.status_code == 403:
            raise HTTPException(status_code=403, detail="GitHub API rate limit exceeded")
        if response.status_code >= 400:
            raise HTTPException(status_code=502, detail="GitHub API error")
        return response.json()

    def get_repo_info(self, owner: str, repo: str) -> Dict:
        return self.api_get(f"https://api.github.com/repos/{owner}/{repo}")

    def get_repo_tree(self, owner: str, repo: str, branch: str) -> List[Dict]:
        tree_url = (
            f"https://api.github.com/repos/{owner}/{repo}/git/trees/"
            f"{quote(branch, safe='')}?recursive=1"
        )
        payload = self.api_get(tree_url)
        tree = payload.get("tree")
        if not tree:
            return []
        return tree

    def fetch_raw_file(self, owner: str, repo: str, branch: str, path: str) -> Optional[str]:
        raw_url = (
            f"https://raw.githubusercontent.com/{owner}/{repo}/"
            f"{quote(branch, safe='/')}/{quote(path)}"
        )
        response = requests.get(raw_url, timeout=self.timeout)
        if response.status_code != 200:
            return None
        text = response.text
        if len(text) > MAX_FILE_BYTES:
            return text[:MAX_FILE_BYTES]
        return text
