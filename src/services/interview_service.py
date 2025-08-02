import asyncio
from typing import Dict, Optional
from app.models.interview import InterviewState
from app.models.message import MessageRequest, MessageResponse
from app.core.config import AppConfig
from app.agents.llm_agent import run_interview_agent


class InterviewService:
    def __init__(self, app_config: AppConfig):
        self.app_config = app_config
        self.session_states: Dict[str, InterviewState] = {}

    def get_or_create_state(self, session_id: str) -> InterviewState:
        if session_id not in self.session_states:
            self.session_states[session_id] = InterviewState(
                current_question="Explain how HashMap works in Java."
            )
        return self.session_states[session_id]

    def update_current_question(self, session_id: str, new_question: str):
        state = self.get_or_create_state(session_id)
        state.current_question = new_question

    def get_current_question(self, session_id: str) -> str:
        return self.get_or_create_state(session_id).current_question

    async def process_student_message(self, request: MessageRequest) -> MessageResponse:
        state = self.get_or_create_state(request.sessionId)
        state.last_student_message = request.message

        system_prompt = f"""
You are a backend interview assistant helping students think and learn.

Context:
- Student is answering this question: "{state.current_question}"
- If student is making a mistake, correct them gently but let them think further.
- Give hints when needed.
- Keep the tone encouraging and constructive.
- Your responses must be short, actionable, and sound like a live conversation.
""".strip()

        user_input = f'''
Student said: "{request.message}"
Now respond like a mock interview assistant as per the above guidelines.
'''.strip()

        ai_reply = await run_interview_agent(
            api_key=self.app_config.openai_api_key,
            prompt=system_prompt,
            user_input=user_input
        )

        state.last_ai_response = ai_reply

        print(f"state.currentQuestion: {state.current_question}")
        print(f"state.studentLastMessage: {state.last_student_message}")
        print(f"state.lastAIResponse: {state.last_ai_response}")

        return MessageResponse(message=ai_reply or "")

    def get_latest_response(self, session_id: str) -> Optional[MessageResponse]:
        state = self.session_states.get(session_id)
        if state and state.last_ai_response:
            return MessageResponse(message=state.last_ai_response)
        return None
