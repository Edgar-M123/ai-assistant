from agents import Agent, WebSearchTool

date_planning_agent = Agent(
    name="date_planning_agent",
    instructions="You are an agent dedicated to planning the best dates.",
    tools=[WebSearchTool()]
)
