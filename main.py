from contextlib import asynccontextmanager
from datetime import date, datetime
from enum import Enum
from typing import Annotated, TypeVar
from agents import Runner, function_tool, Agent, WebSearchTool
from dotenv import load_dotenv
import os
import asyncio
from fastapi import FastAPI
from psycopg.rows import class_row 
from pydantic import BaseModel, TypeAdapter
import psycopg

T = TypeVar("T", covariant=True)

_ = load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
assert OPENAI_API_KEY is not None, "Missing API Key"

conn_string = os.environ.get("DB_CONN_STRING")
assert conn_string is not None, "Missing PG connection string"

class RoleEnum(str, Enum):
    user = 'user'
    assistant = 'assistant'

class SessionRow(BaseModel):
    session_id: str
    role: RoleEnum
    content: str
    created_at: datetime

SessionRowsValidator = TypeAdapter(list[SessionRow])

async def init_db():

    print("Initializing DB")

    assert conn_string is not None, "Missing PG connection string"
    async with await psycopg.AsyncConnection.connect(conninfo=conn_string) as conn:

        async with conn.cursor() as cur:

            print("Creating sessions table")
            _ = await conn.execute("""
            CREATE TABLE IF NOT EXISTS public.sessions (
                session_id VARCHAR,
                role VARCHAR,
                content VARCHAR,
                created_at TIMESTAMP
            )
            """)
            print("Sessions table created")


async def get_session(session_id: str) -> list[SessionRow]:
    assert conn_string is not None, "Missing PG connection string"
    async with await psycopg.AsyncConnection.connect(conninfo=conn_string) as conn:

        async with conn.cursor(row_factory=class_row(SessionRow)) as cur:

            _ = await cur.execute("""
            SELECT
                session_id,
                role,
                content,
                created_at
            FROM sessions
            WHERE session_id = %s
            ORDER BY created_at ASC;
            """, (session_id,))

            session_rows = await cur.fetchall()

        return session_rows

async def save_session(session_row: SessionRow) -> None:

    assert conn_string is not None, "Missing PG connection string"
    async with await psycopg.AsyncConnection.connect(conninfo=conn_string) as conn:

        async with conn.cursor(row_factory=class_row(SessionRow)) as cur:

            _ = await cur.execute("""
            INSERT INTO sessions (session_id, role, content, created_at)
            VALUES ( %s, %s, %s, %s );
            """, (session_row.session_id, session_row.role, session_row.content, session_row.created_at))

        return


@function_tool
async def test_tool(a: Annotated[str, "Test variable a"], bb: Annotated[str, "test var bbb"], ccc: int = 3) -> str:
    """Test tool docstring"""

    return "hey"

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)

class PromptBody(BaseModel):
    text: str
    session_id: str


@app.post("/prompt")
async def post_prompt(prompt: PromptBody):

    print("Hello from ai-assistant!")
    latest_chat = SessionRow(
        session_id=prompt.session_id,
        role=RoleEnum.user,
        content=prompt.text,
        created_at=datetime.now()
    )

    session_data = await get_session(prompt.session_id)

    prompt.text = f"Previous context: {session_data},\nUser: { prompt.text }"

    agent = Agent(
        name="assistant",
        instructions="You are a helpful assistant",
        tools=[test_tool, WebSearchTool()]
    )
    print(f"agent_func_schemas: { agent.tools }")

    result = await Runner.run(agent, prompt.text)
    agent_chat = SessionRow(
        session_id=prompt.session_id,
        role=RoleEnum.assistant,
        content=str(result.final_output),
        created_at=datetime.now()
    )
    print(f"Responses: { result.raw_responses }")

    await save_session(latest_chat)
    await save_session(agent_chat)

    return {"response": result.final_output}

