import json
import asyncio
from typing import Callable, Awaitable, List
from app.models.question import Question
from app.services.interview_service import InterviewService
from app.core.config import AppConfig
from app.prompt.prompts import QUESTION_GENERATION_PROMPT
from app.utils.format import format_output
from app.agents.llm_agent import (
    run_question_generation,
    run_question_streaming_chunks
)


class QuestionService:
    def __init__(self, interview_service: InterviewService, app_config: AppConfig):
        self.interview_service = interview_service
        self.app_config = app_config

    async def generate_question(self) -> Question | None:
        print("generate_question")

        try:
            response = await run_question_generation(
                api_key=self.app_config.openai_api_key,
                prompt=QUESTION_GENERATION_PROMPT,
                user_input="Generate question according to the prompt"
            )
            print(response)

            # Try to parse the LLM response as JSON into a Question object
            data = json.loads(response)
            question = Question(**data)

            # Update InterviewService with new question
            self.interview_service.update_current_question("123", question.questionDescription)
            return question

        except Exception as e:
            print(f"Error parsing response: {str(e)}")
            return None

    async def generate_question_streaming(self, on_chunk: Callable[[str], Awaitable[None]]):
        print("starting question")

        buffer: List[str] = []

        async for chunk in run_question_streaming_chunks(
            api_key=self.app_config.openai_api_key,
            prompt=QUESTION_GENERATION_PROMPT,
            user_input="Generate question according to the prompt"
        ):
            buffer.append(chunk)

            if len(buffer) >= 10:
                combined = "".join(buffer)
                await on_chunk(combined)
                buffer.clear()

            print(chunk, end="")

        if buffer:
            combined = "".join(buffer)
            await on_chunk(combined)
