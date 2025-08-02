from fastapi import FastAPI, Body, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Allow CORS for frontend
origins = [
    "http://localhost:8080"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Data models
class MessageRequest(BaseModel):
    sessionId: str
    message: str

class MessageResponse(BaseModel):
    sessionId: str
    response: str

# Mock interview service
class InterviewService:
    def __init__(self):
        self.responses = {}

    async def process_student_message(self, request: MessageRequest) -> MessageResponse:
        # Mock processing logic
        reply = f"Echo: {request.message}"
        self.responses[request.sessionId] = reply
        return MessageResponse(sessionId=request.sessionId, response=reply)

    def get_latest_response(self, session_id: str) -> Optional[MessageResponse]:
        if session_id in self.responses:
            return MessageResponse(sessionId=session_id, response=self.responses[session_id])
        return None

    def update_current_question(self, session_id: str, question: str):
        self.responses[session_id] = f"Updated question: {question}"

# Inject service
interview_service = InterviewService()

# Routes
@app.post("/interview/message")
async def handle_student_message(request: MessageRequest):
    return await interview_service.process_student_message(request)

@app.get("/interview/response")
def get_latest_response(sessionId: str = Query(...)):
    return interview_service.get_latest_response(sessionId)

@app.put("/interview/question")
def update_question(
    sessionId: str = Query(...),
    question: str = Body(...)
):
    interview_service.update_current_question(sessionId, question)
    return {"message": f"Current question updated successfully for session: {sessionId}"}
