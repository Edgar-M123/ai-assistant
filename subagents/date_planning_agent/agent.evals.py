from datetime import datetime
from services.db_service import SessionRow, RoleEnum
from project_types.eval_types import AgentTestCase


test_cases: list[AgentTestCase] = [
    AgentTestCase(
        id="test_1",
        context=[
            SessionRow(
                session_id="test_1_1",
                role=RoleEnum.user,
                content="Can you please find some cool events happening this weekend that we would like?",
                created_at=datetime(2026, 2, 12)
            )
        ],
        expected_result="The agent should use the WebSearchTool to search for Toronto events happening from Feb 13, 2026 - Feb 15, 2026."
    )
]
