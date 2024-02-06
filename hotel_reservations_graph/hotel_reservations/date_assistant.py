from datetime import datetime, timedelta
from typing import Any

from langchain import hub
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.tools import tool
from langchain_experimental.tools import PythonREPLTool
from langchain_openai import ChatOpenAI


@tool
def distance_to_week_day(date_str: str, weekday: int) -> int:
    """Calculate the number of days until the given weekday."""
    date = datetime.strptime(date_str, "%Y-%m-%d")
    d = (weekday - date.weekday()) % 7
    return d if d != 7 else 0


class AddDayToDateInput(BaseModel):
    date_str: str = Field(description="The date to add to, in the format YYYY-MM-DD")
    days: int = Field(
        description="The number of days to add to the date, Examples: 3, 11, -5. '3 + 2' is NOT a valid"
    )


@tool(args_schema=AddDayToDateInput)
def add_days_to_date(date_str: str, days: int) -> str:
    """Add days to a date. Days argument MUST be a single number."""
    date = datetime.strptime(date_str, "%Y-%m-%d")
    new_date = date + timedelta(days=days)
    return new_date.strftime("%Y-%m-%d")


@tool
def evaluate_math_expression(expression: str) -> str:
    """Evaluate a math expression."""
    return eval(expression)


class DateAssistantOptions:
    def __init__(
        self,
        model: str = "gpt-4",
        temperature: float = 0.0,
    ) -> None:
        self.model = model
        self.temperature = temperature


def default_llm(options: DateAssistantOptions):
    return ChatOpenAI(model=options.model, temperature=options.temperature)


def create_date_assistant(options=DateAssistantOptions(), llm=None):
    instructions = """
    You are a powerful date assistant. You can help users with date-related questions.
    You have some tools at your disposal to help you answer questions.
    You can also write and execute python code to answer the questions. Use this only as last resort.
    You have access to a python REPL, which you can use to execute python code.

    IMPORTANT:
    Consider weekends to start on Friday and end on Sunday. The weekday of a weekend is 4.
    Monday=0, Tuesday=1, Wednesday=2, Thursday=3, Friday=4, Saturday=5, Sunday=6
    Consider weeks to start on Monday and end on Sunday.
    Don't pass expressions as arguments to the tools. The arguments must be single numbers or strings.
    You can use the 'evaluate_math_expression' tool to evaluate math expressions.
    ===

    Your response MUST be in JSON format using the following schema:
    {{
    "date": "YYYY-MM-DD"
    }}

    Good Response Example:
    {{
    "date": "2024-02-03"
    }}

    Bad Response Example:
    Here is the result:
    {{
    "date": "2024-02-03"
    }}

    """
    base_prompt = hub.pull("langchain-ai/openai-functions-template")
    prompt = base_prompt.partial(instructions=instructions)

    if llm is None:
        llm = default_llm(options)

    replTool = PythonREPLTool()
    tools = [
        evaluate_math_expression,
        add_days_to_date,
        distance_to_week_day,
        replTool,
    ]
    agent: Any = create_openai_functions_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    return agent_executor
