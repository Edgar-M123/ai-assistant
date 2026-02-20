from services.db_service import DBService
from agents import Agent


class AgentService:
    
    @classmethod
    async def get_agents(cls) -> dict[str, Agent]:
        agent_params = await DBService.get_agents()

        agents = {params.name: Agent(
            name=params.name,
            handoff_description=params.description,
            instructions=params.description,
            tools=[]
        ) for params in agent_params}
        assert "root_agent" in agents.keys(), "Missing root_agent"

        return agents


