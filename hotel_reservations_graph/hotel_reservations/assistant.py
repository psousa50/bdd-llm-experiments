import functools
from datetime import datetime
from typing import Any, Callable, Union

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, MessageGraph

from hotel_reservations.core import find_hotels, make_reservation
from hotel_reservations.date_assistant import create_date_assistant

FINISH = "FINISH"


def default_llm():
    return ChatOpenAI(
        model="gpt-4",
        temperature=0.0,
    )


def current_date():
    return datetime.now().date()


User = Callable[[list[BaseMessage]], Union[BaseMessage, list[BaseMessage]]]


def real_user_node(_: list[BaseMessage]) -> Union[BaseMessage, list[BaseMessage]]:
    return HumanMessage(content=FINISH)


def date_assistant_builder():
    date_assistant = create_date_assistant()

    def fn(query: str):
        response = date_assistant.invoke({"input": query})
        return response

    date_assistant_builder.__annotations__ = fn.__annotations__
    date_assistant_builder.__name__ = fn.__name__
    return fn


class HotelReservationsAssistantDependencies:
    def __init__(
        self,
        make_reservation=make_reservation,
        find_hotels=find_hotels,
        current_date=current_date,
        llm=default_llm(),
    ) -> None:
        self.make_reservation = make_reservation
        self.find_hotels = find_hotels
        self.current_date = current_date
        self.llm = llm


def assistant_agent(
    dependencies: HotelReservationsAssistantDependencies,
):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                SYSTEM_PROMPT,
            ),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    prompt = prompt.partial(current_date=str(dependencies.current_date()))
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
        StructuredTool.from_function(
            func=date_assistant_builder(),
            name="date_assistant",
            description="""
            Useful to calculate dates.
            The query should be in natural language and it MUST include explicitly the today's date.
            Example: 'Today is 2024-02-03, what day is 3 days from now?'
            """,
        ),
    ]
    agent: Any = create_openai_functions_agent(dependencies.llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools)
    return executor


def assistant_node(agent, messages: list[BaseMessage]):
    result = agent.invoke({"messages": messages})
    return AIMessage(content=result["output"])


def should_continue(max_iterations: int, messages):
    if len(messages) > max_iterations:
        return "end"
    elif messages[-1].content == FINISH:
        return "end"
    else:
        return "continue"


def hotel_reservations_assistant(
    user: User = real_user_node,
    dependencies=HotelReservationsAssistantDependencies(),
    options={
        "max_iterations": 10,
    },
):
    workflow = MessageGraph()

    agent = assistant_agent(dependencies)
    workflow.add_node("assistant", functools.partial(assistant_node, agent))
    workflow.add_node("user", user)
    workflow.set_entry_point("assistant")
    workflow.add_edge("assistant", "user")
    workflow.add_conditional_edges(
        "user",
        functools.partial(should_continue, options["max_iterations"]),
        {
            "end": END,
            "continue": "assistant",
        },
    )

    return workflow.compile()


SYSTEM_PROMPT = """
You are a helpful hotel reservations assistant.
Your job is to help users book hotel rooms.

Today is {current_date}.

You should always ask the user for the information needed to make the reservation, don't guess it.

Consider weekends to be from Friday to Sunday.

The name of the guest is mandatory, you nust ask for it.
"""
