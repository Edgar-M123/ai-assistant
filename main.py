from contextlib import asynccontextmanager
from datetime import datetime
from agents import Runner 
from dotenv import load_dotenv
import os
import asyncio
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from services.db_service import DBService, SessionRow, RoleEnum, SessionRowsValidator
from subagents.root_agent.agent import root_agent

_ = load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):

    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    assert OPENAI_API_KEY is not None, "Missing API Key"

    await DBService.init()
    yield


app = FastAPI(lifespan=lifespan)

class PromptBody(BaseModel):
    text: str
    session_id: str


@app.post("/prompt")
async def post_prompt(prompt: PromptBody, background_tasks: BackgroundTasks):

    session_data = await DBService.get_session(prompt.session_id)

    latest_chat = SessionRow(
        session_id=prompt.session_id,
        role=RoleEnum.user,
        content=prompt.text,
        created_at=datetime.now()
    )
    background_tasks.add_task(DBService.save_session, latest_chat)

    prompt.text = f"Previous context: {SessionRowsValidator.dump_json(session_data)},\nLatest User Chat: { prompt.text }"
    print(f"Prompt test: {prompt.text}")

    result = await Runner.run(root_agent, prompt.text)
    agent_chat = SessionRow(
        session_id=prompt.session_id,
        role=RoleEnum.assistant,
        content=str(result.final_output),
        created_at=datetime.now()
    )
    background_tasks.add_task(DBService.save_session, agent_chat)

    print(f"Responses: { result.raw_responses }")

    return {"response": result.final_output}

