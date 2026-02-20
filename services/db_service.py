import os
import psycopg
from psycopg.rows import class_row
from datetime import datetime

from project_types.agent_types import AgentParams
from project_types.eval_types import AgentTestCase
from project_types.db_types import SessionRow


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

                print("Creating agents table")
                _ = await cur.execute("""
                CREATE TABLE IF NOT EXISTS public.agents (
                    name VARCHAR,
                    description VARCHAR,
                    instructions VARCHAR,
                    parent_agent VARCHAR,
                    tools VARCHAR[],
                    created_at TIMESTAMP,
                    version TIMESTAMP
                );
                """)
                print("Agents table created")

                # if no agents present, create a default one
                agents_query = await cur.execute("""
                SELECT * FROM public.agents;
                """)

                agents = await agents_query.fetchall()
                if len(agents) == 0:
                    print("No agents right now. Creating a default root agent")
                    _ = await cur.execute("""
                    INSERT INTO public.agents (name, description, instructions, parent_agent, tools, created_at, version)
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """, ("root_agent", "Root agent that interfaces with the user", "You are a helpful assistant", None, [], datetime.now(), datetime.now() ))


                print("Creating test cases table")
                _ = await cur.execute("""
                CREATE TABLE IF NOT EXISTS public.test_cases (
                    id VARCHAR,
                    agent_name VARCHAR,
                    test_case_json JSONB,
                    created_at TIMESTAMP
                );
                """)

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
    
    @classmethod
    async def get_agents(cls) -> list[AgentParams]:

        async with await psycopg.AsyncConnection.connect(conninfo=cls.conn_string) as conn:

            async with conn.cursor(row_factory=class_row(AgentParams)) as cur:

                agent_params_query = await cur.execute("""
                WITH ranked as (
                    SELECT
                        *,
                        RANK() OVER (PARTITION BY name ORDER BY version desc) as version_num
                    FROM public.agents
                )
                SELECT 
                    name,
                    description,
                    instructions,
                    parent_agent,
                    tools,
                    created_at,
                    version
                FROM ranked WHERE version_num = 1;
                """)

                agent_params = await agent_params_query.fetchall()

            return agent_params

    @classmethod
    async def add_test_case(cls, test_case: AgentTestCase) -> bool:

        async with await psycopg.AsyncConnection.connect(conninfo=cls.conn_string) as conn:

            async with conn.cursor(row_factory=class_row(AgentParams)) as cur:

                _ = await cur.execute("""
                INSERT INTO public.test_cases (id, agent_name, test_case_json, created_at)
                VALUES (%s, %s, %s, %s);
                """, (test_case.id, "root_agent", test_case.model_dump_json(), datetime.now()) )

            return True

