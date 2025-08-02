from pydantic import BaseModel
from typing import List, Dict, Optional
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
import json
from dotenv import load_dotenv
import os

from question_generation_prompt import QUESTION_GENERATION_PROMPT
from memory.session import get_session

load_dotenv()


class Question(BaseModel):
    questionId: int
    questionTitle: str
    questionDescription: str
    constraints: List[str]
    example: Dict[str, List[str] | str]
    hints: List[str]
    tags: List[str]
    difficulty: str


class QuestionService:
    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            api_key=openai_api_key
        )

    async def generate_question(self, session_id: str) -> Optional[Question]:
        print("generate_question")

        try:
            result = await self.llm.ainvoke([
                SystemMessage(content=QUESTION_GENERATION_PROMPT),
                HumanMessage(content="Generate question according to the prompt")
            ])

            print("LLM result:", result.content)

            try:
                data = json.loads(result.content)
                question = Question(**data)
                session = get_session(session_id)
                session["question"] = question.dict()
                print("Question stored in session:", session)
                return question

            except Exception as parse_error:
                print("Error parsing structured question:", parse_error)
                return None

        except Exception as e:
            print("Error invoking LLM:", str(e))
            return None
