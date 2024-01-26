import logging

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI

from hotel_reservations.callbacks import LLMStartHandler
from hotel_reservations.dependencies import (
    HotelReservationsAssistantDependencies,
)

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
        self.handler = LLMStartHandler()

    def invoke(self, query: str, session_id: str = "foo"):
        response = self.agent.invoke(
            {"input": query},
            config={
                "configurable": {"session_id": session_id},
                "callbacks": [self.handler],
            },
        )
        logger.debug(f"LLM Response: {response}")
        return response

    def build_agent(
        self,
        dependencies: HotelReservationsAssistantDependencies,
    ):
        model = ChatOpenAI(model="gpt-4", temperature=0.0)
        tools = self.build_tools(dependencies)
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        logger.info(f"Prompt: {prompt}")
        agent = create_openai_functions_agent(model, tools, prompt)

        message_history = ChatMessageHistory()
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=self.verbose,
            return_intermediate_steps=True,
        )

        agent_with_chat_history = RunnableWithMessageHistory(
            agent_executor,
            lambda session_id: message_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )

        return agent_with_chat_history

    def build_tools(
        self,
        dependencies: HotelReservationsAssistantDependencies,
    ):
        tools = [
            StructuredTool.from_function(
                func=dependencies.find_hotels,
                name="find_hotels",
                description="Useful to find hotels near a location.",
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
            StructuredTool.from_function(
                func=dependencies.current_date,
                name="current_date",
                description="Useful to get the current date.",
            ),
        ]
        return tools


SYSTEM_PROMPT = """
You have a list of tools that you can use to help you make a reservation.
Don't EVER call the same tool twice with the same arguments, the response will ALWAYS be the same.
You should NEVER try to guess any information needed to make a reservation.
if you realize that you cannot make the reservation, you should say it.
When you have all the information needed to make the reservation, show the user the reservation details, including the price and ask for confirmation.
If the user confirms, make the reservation.
"""  # noqa E501
