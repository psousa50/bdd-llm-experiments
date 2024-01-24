from langchain import hub
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI

from bdd_llm.log import Log
from hotel_reservations.dependencies import HotelReservationsAssistantDependencies


class HotelReservationsAssistant:
    def __init__(
        self,
        dependencies=HotelReservationsAssistantDependencies(),
        verbose=False,
    ):
        self.verbose = verbose

        self.log = Log("HotelReservationsAssistant")
        self.agent = self.build_agent(dependencies)

    def invoke(self, query: str, session_id: str = "foo"):
        response = self.agent.invoke(
            {"input": query},
            config={"configurable": {"session_id": session_id}},
        )
        self.log.verbose("RESPONSE", response)
        return response

    def build_agent(self, dependencies: HotelReservationsAssistantDependencies):
        model = ChatOpenAI(model="gpt-4", temperature=0.0)
        tools = self.build_tools(dependencies)
        prompt = hub.pull("hwchase17/openai-functions-agent")
        agent = create_openai_functions_agent(model, tools, prompt)

        message_history = ChatMessageHistory()
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=self.verbose)

        agent_with_chat_history = RunnableWithMessageHistory(
            agent_executor,
            lambda session_id: message_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )

        return agent_with_chat_history

    def build_tools(self, dependencies: HotelReservationsAssistantDependencies):
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
                func=dependencies.current_date,
                name="current_date",
                description="Useful to get the current date.",
            ),
        ]
        return tools
