"""Compare Python dataclasses with validation of incoming request data."""
from dataclasses import dataclass
from pydantic import BaseModel, ConfigDict, Field


@dataclass
class PlainRequest:
    text: str
    max_results: int


class SearchRequest(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    text: str = Field(min_length=1)
    max_results: int = Field(ge=1, le=10)
