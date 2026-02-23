import json
import os
import re
from typing import Dict, List, Optional

from constants import (
    BINARY_EXTENSIONS,
    EXT_TECH,
    IMPORTANT_ROOT_FILES,
    MAX_FILE_BYTES,
    MAX_FILES,
    MAX_TOTAL_CHARS,
    SKIP_DIR_PREFIXES,
    SKIP_FILE_NAMES,
    TECH_HINTS,
)


class RepositoryAnalyzer:
    def __init__(
        self,
        max_file_bytes: int = MAX_FILE_BYTES,
        max_total_chars: int = MAX_TOTAL_CHARS,
        max_files: int = MAX_FILES,
    ):
        self.max_file_bytes = max_file_bytes
        self.max_total_chars = max_total_chars
        self.max_files = max_files

    def is_binary_path(self, path: str) -> bool:
        lowered = path.lower()
        if os.path.basename(lowered) in SKIP_FILE_NAMES:
            return True
        if any(lowered.startswith(prefix) for prefix in SKIP_DIR_PREFIXES):
            return True
        _, ext = os.path.splitext(lowered)
        return ext in BINARY_EXTENSIONS

    def score_path(self, path: str) -> int:
        lowered = path.lower()
        base = os.path.basename(lowered)
        if base in IMPORTANT_ROOT_FILES and "/" not in lowered:
            return 100
        if base.startswith("readme"):
            return 95
        if lowered.startswith("docs/"):
            return 60
        if lowered.startswith(("src/", "lib/", "app/")):
            return 50
        if "/" not in lowered:
            return 40
        return 10

    def select_files(self, tree: List[Dict]) -> List[Dict]:
        candidates = []
        for entry in tree:
            if entry.get("type") != "blob":
                continue
            path = entry.get("path", "")
            if not path or self.is_binary_path(path):
                continue
            size = entry.get("size", 0)
            if size and size > self.max_file_bytes:
                continue
            candidates.append({"path": path, "size": size, "score": self.score_path(path)})

        candidates.sort(key=lambda item: (-item["score"], item["size"]))
        return candidates[: self.max_files]

    def build_tree_outline(self, paths: List[str]) -> str:
        top_level_dirs = set()
        top_level_files = []
        for path in paths:
            parts = path.split("/")
            if len(parts) == 1:
                top_level_files.append(parts[0])
            else:
                top_level_dirs.add(parts[0] + "/")

        top_level_dirs = sorted(top_level_dirs)[:12]
        top_level_files = sorted(set(top_level_files))[:12]

        outline = "Top-level directories: " + (
            ", ".join(top_level_dirs) if top_level_dirs else "(none)"
        )
        outline += "\nTop-level files: " + (
            ", ".join(top_level_files) if top_level_files else "(none)"
        )
        return outline

    def detect_technologies(self, tree_paths: List[str], file_snippets: Dict[str, str]) -> List[str]:
        found = set()
        for path in tree_paths:
            lowered = path.lower()
            base = os.path.basename(lowered)
            if base in TECH_HINTS:
                found.add(TECH_HINTS[base])
            _, ext = os.path.splitext(lowered)
            if ext in EXT_TECH:
                found.add(EXT_TECH[ext])

        for path, content in file_snippets.items():
            if path.lower().endswith("package.json"):
                try:
                    data = json.loads(content)
                    if "dependencies" in data or "devDependencies" in data:
                        found.add("npm")
                except json.JSONDecodeError:
                    continue

        return sorted(found)

    def build_prompt(self, tree_outline: str, file_snippets: Dict[str, str]) -> str:
        sections = [
            "You are analyzing a GitHub repository. Use the provided files and tree to summarize the project.",
            "Return a JSON object with keys: summary, technologies, structure.",
            "summary: 2-4 sentences. technologies: list of strings. structure: 1-3 sentences.",
            "Avoid markdown in the JSON output.",
            "",
            "Repository tree:",
            tree_outline,
            "",
            "Selected files:",
        ]

        total_chars = 0
        for path, content in file_snippets.items():
            remaining = self.max_total_chars - total_chars
            if remaining <= 0:
                break
            snippet = content[: min(len(content), remaining)]
            sections.append(f"\n---\nFile: {path}\n{snippet}")
            total_chars += len(snippet)

        return "\n".join(sections)

    def parse_llm_response(self, text: str) -> Optional[Dict[str, object]]:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None
        return None

    def build_fallback_summary(self, technologies: List[str], tree_outline: str) -> Dict[str, object]:
        return {
            "summary": "Summary unavailable from LLM response. Review the repository files for details.",
            "technologies": technologies,
            "structure": tree_outline.replace("\n", " "),
        }
