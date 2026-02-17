import os
from enum import Enum
import psycopg
from psycopg.rows import class_row
from pydantic import BaseModel, TypeAdapter, ConfigDict
from datetime import datetime

class RoleEnum(str, Enum):
    user = 'user'
    assistant = 'assistant'

class SessionRow(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    session_id: str
    role: RoleEnum
    content: str
    created_at: datetime

SessionRowsValidator = TypeAdapter(list[SessionRow])

class DBService:
    conn_string: str

    @classmethod
    async def init(cls):
        conn_string = os.environ.get("DB_CONN_STRING")
        assert conn_string is not None, "missing db connection string"

        cls.conn_string = conn_string

        async with await psycopg.AsyncConnection.connect(conninfo=cls.conn_string) as conn:

            async with conn.cursor() as cur:

                print("Creating sessions table")
                _ = await cur.execute("""
                CREATE TABLE IF NOT EXISTS public.sessions (
                    session_id VARCHAR,
                    role VARCHAR,
                    content VARCHAR,
                    created_at TIMESTAMP
                )
                """)
                print("Sessions table created")


    @classmethod
    async def get_session(cls, session_id: str) -> list[SessionRow]:
        async with await psycopg.AsyncConnection.connect(conninfo=cls.conn_string) as conn:

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

    @classmethod
    async def save_session(cls, session_row: SessionRow) -> None:

        print("Saving session data")

        async with await psycopg.AsyncConnection.connect(conninfo=cls.conn_string) as conn:

            async with conn.cursor(row_factory=class_row(SessionRow)) as cur:

                _ = await cur.execute("""
                INSERT INTO sessions (session_id, role, content, created_at)
                VALUES ( %s, %s, %s, %s );
                """, (session_row.session_id, session_row.role, session_row.content, session_row.created_at))

            return None

