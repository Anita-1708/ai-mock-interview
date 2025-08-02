import openai
from typing import AsyncGenerator

async def run_question_generation(api_key: str, prompt: str, user_input: str) -> str:
    openai.api_key = api_key
    response = await openai.ChatCompletion.acreate(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content.strip()

async def run_question_streaming_chunks(
    api_key: str,
    prompt: str,
    user_input: str
) -> AsyncGenerator[str, None]:
    openai.api_key = api_key
    response = await openai.ChatCompletion.acreate(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_input}
        ],
        stream=True
    )
    async for chunk in response:
        if "choices" in chunk:
            content = chunk["choices"][0]["delta"].get("content", "")
            if content:
                yield content
