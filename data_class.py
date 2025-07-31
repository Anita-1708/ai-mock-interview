from pydantic import BaseModel

class MessageRequest(BaseModel):
    session_id : str
    user_input : str