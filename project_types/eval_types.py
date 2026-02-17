from typing import Annotated
from pydantic import BaseModel

from services.db_service import SessionRow

class AgentTestCase(BaseModel):
    id: Annotated[str, "test case ID"]
    context: Annotated[list[SessionRow], f'List of inputs using the following model: {SessionRow.model_fields}. This is the context that the agent will be responding to.']
    expected_result: Annotated[str, "Description of the expected result of this test case"]
