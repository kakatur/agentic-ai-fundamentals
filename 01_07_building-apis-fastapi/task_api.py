"""A small local FastAPI app with request validation."""
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


class TaskRequest(BaseModel):
    text: str = Field(min_length=1)


class TaskResponse(BaseModel):
    text: str
    word_count: int


def count_words(text: str) -> int:
    return len(text.split())


@app.post('/tasks', response_model=TaskResponse)
def create_task(request: TaskRequest) -> TaskResponse:
    return TaskResponse(text=request.text, word_count=count_words(request.text))
