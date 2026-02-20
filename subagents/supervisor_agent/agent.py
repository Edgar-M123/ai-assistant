from agents import Agent, GuardrailFunctionOutput, RunContextWrapper, Runner, TResponseInputItem, input_guardrail 
from pydantic import BaseModel
from project_types.eval_types import AgentTestCase
from services.db_service import DBService

class SupervisorOutput(BaseModel):
    negative_signal: bool
    signal_type: str
    summary: str
    proposed_solution: str
    test_case: AgentTestCase

supervisor_instructions = """
Your job is to determine if the user is providing negative signals in response to the AI assistant's behaviour.

These are the negative signals to look for:
- **Repeated rephrasing**: The user is has repeated the same question or request multiple times
- **Escalating tone**: The user talks about how the AI's assistance is "broke", "terrible", "frustrating", etc.
- **Backtracking**: The user asks the AI to undo tasks or revert to a previous state.
- **Correction**: The user corrects an AI's response.

If the AI output results in negative signals, you must output the following:
negative_signal = true
signal_type: <signal type in all lowercase and underscores, like "repeated_rephrasing">
summary: <1-line summary of what happened>
propose_solution: <1-line answer on how this signal can could have been avoided within the current context>
test_case: <test case to evaluate future AI versions and prevent them from having this behaviour>
"""

supervisor_agent = Agent(
    name="supervisor",
    model="gpt-5-nano",
    handoff_description="Agent that determines whether or not the current interact was against the system instructions or resulted in negative feedback from the user",
    instructions=supervisor_instructions,
    output_type=SupervisorOutput,
)

@input_guardrail
async def supervisor_guardrail(ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]) -> GuardrailFunctionOutput:

    result = await Runner.run(supervisor_agent, input, context=ctx.context)
    print(f"guardrail result: {result.raw_responses}")

    if result.final_output.negative_signal:
        await DBService.add_test_case(result.final_output.test_case)


    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=False # hard coded False because this agent shouldn't block responses if it triggers
    )


