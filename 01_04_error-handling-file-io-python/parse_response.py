"""Parse a simulated AI response and validate its expected shape."""
import json
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class Response(BaseModel):
    model_config = ConfigDict(strict=True, extra='forbid')
    category: Literal['shipping', 'returns', 'other']
    summary: str = Field(min_length=1)


def parse_response(raw: str) -> Response:
    """Raise JSONDecodeError for invalid JSON or ValidationError for bad data."""
    data = json.loads(raw)
    return Response.model_validate(data)


def save_response(response: Response, path: Path) -> None:
    """Save a validated response as human-readable JSON."""
    path.write_text(json.dumps(response.model_dump(), indent=2) + '\n', encoding='utf-8')
