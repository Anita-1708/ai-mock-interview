import asyncio
from typing import Dict, List
from fastapi import WebSocket, WebSocketDisconnect
from urllib.parse import urlparse, parse_qs
from app.services.question_service import QuestionService

class InterviewWebSocketHandler:
    def __init__(self, question_service: QuestionService):
        self.question_service = question_service
        self.channel_sessions: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()

        channel_id = self.extract_channel_id(websocket) or "default"
        print(f"Connection established: channelId={channel_id}")

        if channel_id not in self.channel_sessions:
            self.channel_sessions[channel_id] = []

        self.channel_sessions[channel_id].append(websocket)
        return channel_id

    async def disconnect(self, websocket: WebSocket, channel_id: str):
        self.channel_sessions[channel_id].remove(websocket)
        print(f"Session closed: channelId={channel_id}")

        if not self.channel_sessions[channel_id]:
            del self.channel_sessions[channel_id]
            print(f"🧹 Removed empty channel: {channel_id}")

    async def handle_message(self, websocket: WebSocket, channel_id: str, message: str):
        print(f"Received message | payload={message}")
        try:
            async for chunk in self.question_service.generate_question_streaming():
                await self.broadcast_to_channel(channel_id, chunk)
        except Exception as e:
            print(f"Error in streaming question: {e}")

    async def broadcast_to_channel(self, channel_id: str, message: str):
        for ws in self.channel_sessions.get(channel_id, []):
            if ws.client_state.name == "CONNECTED":
                await ws.send_text(message)

    def extract_channel_id(self, websocket: WebSocket) -> str:
        query = parse_qs(urlparse(str(websocket.url)).query)
        return query.get("channelId", ["default"])[0]
