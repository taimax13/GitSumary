from pydantic import BaseModel


class SummarizeRequest(BaseModel):
    github_url: str
