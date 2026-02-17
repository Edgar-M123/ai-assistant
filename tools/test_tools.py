from agents import function_tool
from typing import Annotated

@function_tool
async def test_tool(a: Annotated[str, "test variable a"], bb: Annotated[str, "test var bbb"], ccc: int = 3) -> str:
    """test tool docstring"""

    result = f"Var a: {a}, var bb: {bb}, var ccc: {ccc}"

    return result
