from pydantic import BaseModel

class MessageRequest(BaseModel):
    sessionId: str
    message: str
