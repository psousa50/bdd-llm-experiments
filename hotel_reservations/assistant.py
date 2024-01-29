import logging

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI

from hotel_reservations.callbacks import LLMStartHandler
from hotel_reservations.dependencies import HotelReservationsAssistantDependencies

logger = logging.getLogger(__name__)


class HotelReservationsAssistant:
    def __init__(
        self,
        dependencies=HotelReservationsAssistantDependencies(),
        verbose=False,
    ):
        self.dependencies = dependencies
        self.verbose = verbose

        self.agent = self.build_agent(dependencies)
        self.chat_history = []
        self.handler = LLMStartHandler()

    def invoke(self, query: str, session_id: str = "foo"):
        response = self.agent.invoke(
            {"input": query, "chat_history": self.chat_history},
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
    ):
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.0,
            openai_api_base="http://localhost:8000",
        )
        tools = self.build_tools(dependencies)
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        logger.debug(f"Agent Prompt: {prompt}")
        agent = create_openai_functions_agent(llm, tools, prompt)

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
                func=dependencies.current_date,
                name="current_date",
                description="Useful to get the current date.",
            ),
            StructuredTool.from_function(
                func=dependencies.current_year,
                name="current_year",
                description="Useful to find the current year.",
            ),
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
            StructuredTool.from_function(
                func=dependencies.calc_reservation_price,
                name="calc_reservation_price",
                description="Useful to calculate the price of a reservation.",
            ),
        ]
        return tools


SYSTEM_PROMPT = """
You have a list of tools that you can use to help you make a reservation.
Don't EVER call the same tool twice with the same arguments, the response will ALWAYS be the same.
You should ask the user for the information needed to make the reservation, don't guess it.
If a date is provided without a year, you should use a tool to find the current year.
If you need to find out the current date, you should use a tool to get it.
The name of the guest is mandatory to make the reservation.
If should try to find out what's the current year, don't assume it.
if you realize that you cannot make the reservation, you should say it.
When you have all the information needed to make the reservation, show the user the reservation details, including the price and ask for confirmation.
If the user confirms, make the reservation.
"""  # noqa E501
