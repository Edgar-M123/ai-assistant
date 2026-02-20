from datetime import datetime
from pydantic import BaseModel


class AgentParams(BaseModel):
    name: str
    description: str
    instructions: str
    tools: list[str]
    parent_agent: str | None
    created_at: datetime
    version: datetime
