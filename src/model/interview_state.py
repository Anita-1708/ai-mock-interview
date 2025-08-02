from typing import Optional
from pydantic import BaseModel

class InterviewState(BaseModel):
    currentQuestion: str
    lastStudentMessage: Optional[str] = None
    lastAIResponse: Optional[str] = None
