from typing import Dict, Optional

from fastapi import HTTPException

from github_client import GitHubRepositoryClient
from nebius_llm_client import NebiusLLMClient
from repository_analyzer import RepositoryAnalyzer
from summarize_response import SummarizeResponse


class RepoSummarizerService:
    def __init__(
        self,
        repo_client: Optional[GitHubRepositoryClient] = None,
        analyzer: Optional[RepositoryAnalyzer] = None,
        llm_client: Optional[NebiusLLMClient] = None,
    ):
        self.repo_client = repo_client or GitHubRepositoryClient()
        self.analyzer = analyzer or RepositoryAnalyzer()
        self.llm_client = llm_client or NebiusLLMClient()

    def summarize(self, github_url: str) -> SummarizeResponse:
        owner, repo = self.repo_client.parse_url(github_url)
        repo_info = self.repo_client.get_repo_info(owner, repo)
        default_branch = repo_info.get("default_branch")
        if not default_branch:
            raise HTTPException(status_code=502, detail="Unable to determine default branch")

        tree = self.repo_client.get_repo_tree(owner, repo, default_branch)
        if not tree:
            raise HTTPException(status_code=404, detail="Repository appears to be empty")

        selected = self.analyzer.select_files(tree)
        file_snippets: Dict[str, str] = {}
        total_chars = 0

        for entry in selected:
            path = entry["path"]
            content = self.repo_client.fetch_raw_file(owner, repo, default_branch, path)
            if not content:
                continue
            remaining = self.analyzer.max_total_chars - total_chars
            if remaining <= 0:
                break
            trimmed = content[:remaining]
            file_snippets[path] = trimmed
            total_chars += len(trimmed)

        tree_paths = [item.get("path", "") for item in tree if item.get("path")]
        tree_outline = self.analyzer.build_tree_outline(tree_paths)
        prompt = self.analyzer.build_prompt(tree_outline, file_snippets)

        llm_text = self.llm_client.chat(prompt)
        response_data = self.analyzer.parse_llm_response(llm_text)

        technologies = self.analyzer.detect_technologies(tree_paths, file_snippets)

        if not response_data:
            response_data = self.analyzer.build_fallback_summary(technologies, tree_outline)

        summary = str(response_data.get("summary", "")).strip()
        structure = str(response_data.get("structure", "")).strip()
        tech_list = response_data.get("technologies")
        if not isinstance(tech_list, list):
            tech_list = technologies

        return SummarizeResponse(
            summary=summary or "No summary provided.",
            technologies=[str(item) for item in tech_list] if tech_list else technologies,
            structure=structure or tree_outline,
        )
