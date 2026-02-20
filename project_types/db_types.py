from enum import Enum
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
