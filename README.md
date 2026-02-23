# GitHub Repo Summarizer

Small FastAPI service that summarizes a public GitHub repository with an LLM.

## Screenshot

![GitSummary screenshot](img/Screenshot%20from%202026-02-23%2007-11-10.png)

## Setup

1. Create and activate a virtual environment (optional but recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set the Nebius API key and model:

```bash
export NEBIUS_API_KEY="your_api_key"
export NEBIUS_MODEL="meta-llama/Llama-3.3-70B-Instruct" 
```

Optional overrides:

```bash
export NEBIUS_API_BASE="https://api.tokenfactory.nebius.com/v1"
```

4. Start the server:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Usage

```bash
curl -X POST http://localhost:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{"github_url": "https://github.com/psf/requests"}'
```

## Model Choice

Default model is `meta-llama/Llama-3.3-70B-Instruct` because it provides strong instruction-following with good summaries while staying widely available on Nebius Token Factory. You can override it via `NEBIUS_MODEL`.

## Repository Processing Approach

- Fetch the repository tree via the GitHub API and skip obvious noise (binary files, lock files, build artifacts, and vendor directories).
- Prioritize README and root config files, then sample files from `src/`, `lib/`, or `app/`.
- Cap total context size (`MAX_TOTAL_CHARS`) and per-file size (`MAX_FILE_BYTES`) to avoid exceeding LLM limits.
- Provide a condensed top-level tree outline plus selected file contents to the LLM.
