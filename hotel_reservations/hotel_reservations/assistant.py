import json
import logging
from typing import Any

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.tools import StructuredTool, tool
from langchain_openai import ChatOpenAI

from hotel_reservations.callbacks import LLMStartHandler
from hotel_reservations.date_assistant import create_date_assistant
from hotel_reservations.dependencies import HotelReservationsAssistantDependencies
from hotel_reservations.function_call_agent_output_parser import (
    FunctionCallAgentOutputParser,
)

logger = logging.getLogger(__name__)

date_assistant = create_date_assistant()


class DateAssistantInput(BaseModel):
    query: str = Field(
        description="""
            The input to the date assistant. It should be in natural language and it MUST include the current date.
            Example: "Today is 2024-04-01. What day is tomorrow?"
        """
    )


@tool(args_schema=DateAssistantInput)
def date_assistant_tool(query: str) -> str:
    """Useful to calculate dates."""
    result = date_assistant.invoke({"input": query})
    print(result)
    json_result = json.loads(result["output"])
    return json_result["date"]


class HotelReservationsAssistant:
    def __init__(
        self,
        llm: BaseLanguageModel,
        dependencies=HotelReservationsAssistantDependencies(),
        verbose=False,
    ):
        self.dependencies = dependencies
        self.verbose = verbose

        self.chat_history = []
        self.handler = LLMStartHandler()

        self.agent = self.build_agent(dependencies, llm)

    def invoke(self, query: str, session_id: str = "foo"):
        response = self.agent.invoke(
            {
                "input": query,
                "chat_history": self.chat_history,
            },
            config={
                "configurable": {"session_id": session_id},
                "callbacks": [self.handler],
            },
        )
        intermediate_steps = format_to_openai_function_messages(
            response["intermediate_steps"]
        )
        self.chat_history.append(HumanMessage(content=query))
        self.chat_history.extend(intermediate_steps)
        self.chat_history.append(AIMessage(content=response["output"]))

        logger.debug(f"LLM Response: {response}")
        return response

    def build_agent(
        self,
        dependencies: HotelReservationsAssistantDependencies,
        llm: BaseLanguageModel,
    ):
        tools = self.build_tools(dependencies)
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
        prompt = prompt.partial(current_date=str(self.dependencies.current_date()))

        logger.debug(f"Agent Prompt: {prompt}")

        if isinstance(llm, ChatOpenAI):
            agent: Any = create_openai_functions_agent(llm, tools, prompt)
        else:
            agent: Any = (
                RunnablePassthrough.assign(
                    agent_scratchpad=lambda x: format_to_openai_function_messages(
                        x["intermediate_steps"]
                    )
                )
                | prompt
                | llm
                | FunctionCallAgentOutputParser()
            )

        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            return_intermediate_steps=True,
            verbose=self.verbose,
        )

        return agent_executor

    def build_tools(
        self,
        dependencies: HotelReservationsAssistantDependencies,
    ):
        tools = [
            StructuredTool.from_function(
                func=dependencies.find_hotels,
                name="find_hotels",
                description="Useful to find hotels by name and/or location.",
            ),
            StructuredTool.from_function(
                func=dependencies.make_reservation,
                name="make_reservation",
                description="Useful to make a reservation.",
            ),
            date_assistant_tool,
            # StructuredTool.from_function(
            #     func=dependencies.calc_reservation_price,
            #     name="calc_reservation_price",
            #     description="Useful to calculate the price of a reservation.",
            # ),
        ]
        return tools


SYSTEM_PROMPT = """
You are a helpful hotel reservations assistant.

The name of the guest is mandatory to make the reservation.

Today is {current_date}.

Consider weekends to start at Friday and end at Sunday.

A stay of 2 days starting today ends the day after tomorrow.

You should always confirm the reservation with the user before making it.

"""  # noqa E501

SYSTEM_PROMPT_2 = """
You are a helpful hotel reservations assistant.
"""  # noqa E501
