from fastapi import APIRouter, UploadFile, HTTPException, FastAPI
from fastapi.responses import JSONResponse
import os
import logging

from ai import processRequest,start_new_interview
from data_class import MessageRequest

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




# Include the router in the app
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)