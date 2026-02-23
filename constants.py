APP_TITLE = "GitHub Repo Summarizer"
REQUEST_TIMEOUT = 60

MAX_FILE_BYTES = 200_000
MAX_TOTAL_CHARS = 120_000
MAX_FILES = 20

BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".svg", ".pdf",
    ".zip", ".tar", ".gz", ".7z", ".rar", ".jar", ".class",
    ".exe", ".dll", ".so", ".dylib", ".bin", ".whl", ".apk",
    ".mp3", ".mp4", ".mov", ".avi", ".mkv", ".wav",
}

SKIP_DIR_PREFIXES = (
    "node_modules/", "dist/", "build/", "target/", "vendor/", "venv/", ".venv/",
    ".git/", ".idea/", ".pytest_cache/", "__pycache__/", "coverage/",
)

SKIP_FILE_NAMES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock", "pipfile.lock", "go.sum",
}

IMPORTANT_ROOT_FILES = {
    "readme.md", "readme.rst", "readme.txt",
    "pyproject.toml", "setup.py", "setup.cfg", "requirements.txt", "requirements-dev.txt",
    "package.json",
    "go.mod", "cargo.toml", "pom.xml", "build.gradle", "build.gradle.kts",
    "gemfile", "composer.json", "makefile", "dockerfile",
    "license", "license.txt", "license.md",
}

TECH_HINTS = {
    "pyproject.toml": "Python",
    "setup.py": "Python",
    "requirements.txt": "Python",
    "package.json": "Node.js",
    "go.mod": "Go",
    "cargo.toml": "Rust",
    "pom.xml": "Java",
    "build.gradle": "Java",
    "build.gradle.kts": "Kotlin",
    "gemfile": "Ruby",
    "composer.json": "PHP",
    "dockerfile": "Docker",
}

EXT_TECH = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".kt": "Kotlin",
    ".rb": "Ruby",
    ".php": "PHP",
    ".cs": ".NET",
    ".cpp": "C++",
    ".c": "C",
    ".swift": "Swift",
}
