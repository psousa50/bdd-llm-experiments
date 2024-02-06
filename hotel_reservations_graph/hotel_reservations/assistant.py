import functools
import logging
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

HOTEL_ASSISTANT = "HOTEL_ASSISTANT"
DATE_ASSISTANT = "DATE_ASSISTANT"
USER = "USER"
FINISH = "FINISH"

logger = logging.getLogger(__name__)


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
    ]
    agent: Any = create_openai_functions_agent(dependencies.llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools)
    return executor


def hotel_assistant_node(agent, messages: list[BaseMessage]):
    result = agent.invoke({"messages": messages})
    return AIMessage(content=result["output"])


def date_assistant_node(date_assistant, messages: list[BaseMessage]):
    print("messages2", messages)
    last_message = messages[-1].content
    result = date_assistant.invoke({"input": last_message})
    return AIMessage(content=result["output"])


def from_user(max_iterations: int, messages):
    if len(messages) > max_iterations:
        return "end"
    elif messages[-1].content == FINISH:
        return "end"
    else:
        return "continue"


def from_assistant(max_iterations: int, messages: list[BaseMessage]):
    print("messages", messages)
    if len(messages) > max_iterations:
        return "end"
    elif DATE_ASSISTANT in messages[-1].content:
        return DATE_ASSISTANT
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
    date_assistant = create_date_assistant()

    workflow.add_node(HOTEL_ASSISTANT, functools.partial(hotel_assistant_node, agent))
    workflow.add_node(
        DATE_ASSISTANT, functools.partial(date_assistant_node, date_assistant)
    )
    workflow.add_node(USER, user)

    workflow.add_edge(DATE_ASSISTANT, HOTEL_ASSISTANT)
    workflow.add_conditional_edges(
        HOTEL_ASSISTANT,
        functools.partial(from_assistant, options["max_iterations"]),
        {
            "end": END,
            DATE_ASSISTANT: DATE_ASSISTANT,
            "continue": USER,
        },
    )
    workflow.add_conditional_edges(
        USER,
        functools.partial(from_user, options["max_iterations"]),
        {
            "end": END,
            "continue": HOTEL_ASSISTANT,
        },
    )

    workflow.set_entry_point(HOTEL_ASSISTANT)

    return workflow.compile()


SYSTEM_PROMPT = """
You are a helpful hotel reservations assistant.
Your job is to help users book hotel rooms.

Today is {current_date}.

You should always ask the user for the information needed to make the reservation, don't guess it.

Consider weekends to be from Friday to Sunday.

The name of the guest is mandatory, you nust ask for it.

You should use the DATE_ASSISTANT to help you with date-related questions.
The DATE_ASSISTANT is NOT a tool function, don't try to call it as a tool function.
When you need to use the DATE_ASSISTANT, you should just respond with "DATE_ASSISTANT", followed by the query:
Example:
DATE_ASSISTANT: Today is 2024-02-03, what is the date 3 days from now?

You should always confirm the reservation with the user before making it.

"""
