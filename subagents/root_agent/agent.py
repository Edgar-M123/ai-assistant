from agents import Agent, WebSearchTool
from tools.test_tools import test_tool

root_agent = Agent(
    name="root_agent",
    instructions="You are a helpful assistant",
    tools=[WebSearchTool(), test_tool]
)
