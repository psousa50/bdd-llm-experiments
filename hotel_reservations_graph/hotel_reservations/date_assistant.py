from typing import Any

from langchain import hub
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_experimental.tools import PythonREPLTool
from langchain_openai import ChatOpenAI


def create_date_assistant():
    instructions = """
    You are a powerful date assistant. You can help users with date-related questions.
    You can write and execute python code to answer the questions.
    You have access to a python REPL, which you can use to execute python code.
    If you get an error, debug your code and try again.
    Only use the output of your code to answer the question. 
    You might know the answer without running any code, but you should still run the code to get the answer.

    Consider weekends to start on Friday and end on Sunday.
    Consider weeks to start on Monday and end on Sunday.

    Your response should be in JSON format using the following format:
    {{
    "date": "YYYY-MM-DD"
    }}
    """
    base_prompt = hub.pull("langchain-ai/openai-functions-template")
    prompt = base_prompt.partial(instructions=instructions)

    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.0,
    )
    tools = [PythonREPLTool()]
    agent: Any = create_openai_functions_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    return agent_executor
