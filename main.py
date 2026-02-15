from typing import Annotated, Callable, Optional
from agents import Runner, function_tool, Agent, WebSearchTool
from dotenv import load_dotenv
import os
import asyncio
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
assert OPENAI_API_KEY is not None, "Missing API Key"

@function_tool
async def test_tool(a: Annotated[str, "Test variable a"], bb: Annotated[str, "test var bbb"], ccc: int = 3) -> str:
    """Test tool docstring"""

    return "hey"

app = FastAPI()

class PromptBody(BaseModel):
    text: str
    session_id: Optional[str] = None

@app.post("/prompt")
async def post_prompt(prompt: PromptBody):

    print("Hello from ai-assistant!")

    agent = Agent(
        name="assistant",
        instructions="You are a helpful assistant",
        tools=[test_tool, WebSearchTool()]
    )
    print(f"agent_func_schemas: { agent.tools }")

    result = await Runner.run(agent, prompt.text)
    print(f"Responses: { result.raw_responses }")

    return {"response": result.final_output}

