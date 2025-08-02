from typing import List
from pydantic import BaseModel


class Example(BaseModel):
    input: str
    output: str


class Question(BaseModel):
    questionId: int
    questionTitle: str
    questionDescription: str
    constraints: List[str]
    example: Example
    hints: List[str]
    tags: List[str]
    difficulty: str
