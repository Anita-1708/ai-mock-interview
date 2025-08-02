from fastapi import WebSocket
from app.websockets.interview_ws_handler import InterviewWebSocketHandler
from app.services.question_service import QuestionService
from app.core.config import AppConfig

question_service = QuestionService(AppConfig())
interview_handler = InterviewWebSocketHandler(question_service)

async def interview_websocket_endpoint(websocket: WebSocket):
    print("WebSocketConfig initialized")
    channel_id = await interview_handler.connect(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            await interview_handler.handle_message(websocket, channel_id, message)
    except Exception:
        await interview_handler.disconnect(websocket, channel_id)
