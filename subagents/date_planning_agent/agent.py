from agents import Agent, WebSearchTool
from tools.test_tools import test_tool

date_planning_agent = Agent(
    name="date_planning_agent",
    instructions="You are an agent dedicated to planning the best dates.",
    tools=[WebSearchTool()]
)
