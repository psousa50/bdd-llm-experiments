from typing import Callable

from langchain import hub
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from bdd_llm.log import Log

from bdd_llm.user import UserProxy
from hotel_reservations.core import MakeReservation
from hotel_reservations.tools import build_tools

StopCondition = Callable[[dict], bool]


class HotelReservationsAssistant:
    def __init__(
        self,
        user_proxy: UserProxy,
        make_reservation: MakeReservation,
        stop_condition: StopCondition = lambda _: False,
        max_iterations: int = 5,
    ):
        self.user_proxy = user_proxy
        self.make_reservation = make_reservation
        self.stop_condition = stop_condition
        self.max_iterations = max_iterations

        self.log = Log("HotelReservationsAssistant")
        self.agent = self.build_agent()

    def start(self):
        query = self.user_proxy.query
        if query == "":
            query = self.user_proxy.get_input("How can I help you?")
        done = False
        iterations = 0
        while not done:
            response = self.agent.invoke(
                {"input": query},
                config={"configurable": {"session_id": "<foo>"}},
            )
            self.log("RESPONSE", response)
            iterations += 1
            if iterations >= self.max_iterations:
                query = "I'm sorry, I can't help you with that."
                done = True
            done = done or self.stop_condition(response)
            if not done:
                output = response["output"]
                query = self.user_proxy.get_input(output)

    def build_agent(self):
        model = ChatOpenAI(model="gpt-4", temperature=0.0)
        tools = build_tools(self.make_reservation)
        prompt = hub.pull("hwchase17/openai-functions-agent")
        agent = create_openai_functions_agent(model, tools, prompt)

        message_history = ChatMessageHistory()
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

        agent_with_chat_history = RunnableWithMessageHistory(
            agent_executor,
            lambda session_id: message_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )

        return agent_with_chat_history
