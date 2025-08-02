from fastapi import APIRouter, UploadFile, HTTPException, FastAPI
from fastapi.responses import JSONResponse
import os
import logging, json

from ai import processRequest,start_new_interview
from data_class import MessageRequest
from question_service import QuestionService, Question

question_service = QuestionService(openai_api_key=os.getenv("OPENAI_API_KEY"))


logger = logging.getLogger(__name__)

# Create FastAPI app instance
app = FastAPI(title="AI Mock Interview API", version="1.0.0")

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Hello World"}


@router.post("/start-new-session")
async def start_new():
    print("start_new_interview")
    result = start_new_interview()
    return {"session_id":result["session_id"],"bot_says": result["output"]}



@router.post("/message-me")
async def process_input(request: MessageRequest):

    print(f"process_input for request {request.session_id} : {request.user_input}")
    result = processRequest(request.user_input,request.session_id)
    return {"processed_result": result}

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict

# Add this to maintain active connections per session
active_connections: Dict[str, WebSocket] = {}


@router.get("/question/{session_id}", response_model=Question | None)
async def get_question(session_id: str):
    print("Generating question")
    return await question_service.generate_question(session_id)


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    active_connections[session_id] = websocket
    print(f"WebSocket connected for session: {session_id}")

    try:
        while True:
            user_input = await websocket.receive_text()
            print(f"Received message from {session_id}: {user_input}")

            # Process interview input via LangGraph
            input_data = json.loads(user_input)

            # Now access 'content'
            content = input_data["content"]
            response = processRequest(content, session_id)
            await websocket.send_text(response)

    except WebSocketDisconnect:
        print(f"WebSocket disconnected for session: {session_id}")
        active_connections.pop(session_id, None)


@router.post("/start-new-session-1")
async def start_new():
    result = start_new_interview()
    return {
        "session_id": result["session_id"],
        "bot_says": result["output"],
        "ws_url": f"/ws/{result['session_id']}"
    }



# Include the router in the app
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)