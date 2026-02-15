from typing import Annotated, Callable
from agents import Runner, function_tool, Agent, WebSearchTool
from dotenv import load_dotenv
import os

@function_tool
def test_tool(a: Annotated[str, "Test variable a"], bb: Annotated[str, "test var bbb"], ccc: int = 3) -> str:
    """Test tool docstring"""

    return "hey"

def main():
    load_dotenv()

    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

    assert OPENAI_API_KEY is not None, "Missing API Key"

    print("Hello from ai-assistant!")

    agent = Agent(
        name="assistant",
        instructions="You are a helpful assistant",
        tools=[test_tool, WebSearchTool()]
    )
    print(f"agent_func_schemas: { agent.tools }")

    result = Runner.run_sync(agent, "Hi, please use the test tool, and find out who was the latest superbowl halftime show performer.")
    print(f"Responses: { result.raw_responses }")



if __name__ == "__main__":
    main()
