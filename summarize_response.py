from typing import List

from pydantic import BaseModel


class SummarizeResponse(BaseModel):
    summary: str
    technologies: List[str]
    structure: str
