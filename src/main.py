from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.websocket.websocket_config import interview_websocket_endpoint

app = FastAPI()  # ✅ This line must be at top level

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.websocket("/interview")
async def interview_ws(websocket: WebSocket):
    await interview_websocket_endpoint(websocket)
