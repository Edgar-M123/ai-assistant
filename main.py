from contextlib import asynccontextmanager
from datetime import datetime
from typing import TypedDict
from agents import Agent, Runner 
from dotenv import load_dotenv
import os
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from services.agent_service import AgentService
from project_types.db_types import SessionRow, RoleEnum, SessionRowsValidator
from services.db_service import DBService
from subagents.supervisor_agent.agent import supervisor_guardrail

_ = load_dotenv()


class AppContext(TypedDict):
    agents: dict[str, Agent]

context: AppContext = {
    "agents": {}
}

@asynccontextmanager
async def lifespan(app: FastAPI): 

    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    assert OPENAI_API_KEY is not None, "Missing API Key"

    await DBService.init()
    context['agents'] = await AgentService.get_agents()
    print(f"agents: {context['agents']}")
    yield

    context['agents'].clear()
    

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

    root_agent = context['agents'].get("root_agent")
    assert root_agent is not None, "Root agent does not exist in agents table."

    root_agent.input_guardrails = [supervisor_guardrail]

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

