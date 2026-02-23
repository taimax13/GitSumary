from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from constants import APP_TITLE
from error_response import ErrorResponse
from repo_summarizer_service import RepoSummarizerService
from summarize_request import SummarizeRequest
from summarize_response import SummarizeResponse

app = FastAPI(title=APP_TITLE)


@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": exc.detail},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": str(exc)},
    )


summarizer_service = RepoSummarizerService()


@app.post("/summarize", response_model=SummarizeResponse, responses={400: {"model": ErrorResponse}})
def summarize_repo(request: SummarizeRequest):
    return summarizer_service.summarize(request.github_url)
