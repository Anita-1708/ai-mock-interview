from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.services.question_service import QuestionService
from app.core.config import AppConfig
from app.prompt.prompts import QUESTION_GENERATION_PROMPT
from app.utils.format import format_output
from app.agents.llm_agent import run_question_agent, run_calculator_agent
from app.models.question import Question

router = APIRouter()

question_service = QuestionService()
app_config = AppConfig()

@router.get("")
async def get_question() -> Question | None:
    print("Generating question")
    return await question_service.generate_question()

@router.get("/1")
async def get_question_streaming():
    print("starting question")
    
    async def generate():
        async for chunk in run_question_agent(app_config.openai_api_key):
            yield chunk

    return StreamingResponse(generate(), media_type="text/plain")
