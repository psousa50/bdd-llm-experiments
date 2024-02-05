import json
import operator
import os
from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import (
    BaseMessage,
    FunctionMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_core.tools import StructuredTool
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolInvocation
from langgraph.prebuilt.tool_executor import ToolExecutor

from hotel_reservations.core import find_hotels, make_reservation

os.environ["LANGCHAIN_PROJECT"] = "Hotel Reservations Graph"


def default_llm():
    return ChatOpenAI(
        model="gpt-4",
        temperature=0.0,
    )


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


class HotelReservationsAssistantDependencies:
    def __init__(
        self,
        make_reservation=make_reservation,
        find_hotels=find_hotels,
        llm=default_llm(),
    ) -> None:
        self.make_reservation = make_reservation
        self.find_hotels = find_hotels
        self.llm = llm


class HotelReservationsAssistant:
    def __init__(
        self,
        dependencies=HotelReservationsAssistantDependencies(),
    ) -> None:
        self.dependencies = dependencies

        tools = self.build_tools(dependencies)
        functions = [convert_to_openai_function(t) for t in tools]
        self.tool_executor = ToolExecutor(tools)
        self.model = self.dependencies.llm.bind_functions(functions)
        self.build_graph()
        system_message = SystemMessage(content=SYSTEM_PROMPT)
        self.state: dict[str, list[BaseMessage]] = {"messages": [system_message]}

    def build_tools(self, dependencies: HotelReservationsAssistantDependencies):
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
        return tools

    def should_continue(self, state):
        messages = state["messages"]
        last_message = messages[-1]
        # If there is no function call, then we finish
        if "function_call" not in last_message.additional_kwargs:
            return "end"
        # Otherwise if there is, we continue
        else:
            return "continue"

    # Define the function that calls the model
    def call_model(self, state):
        messages = state["messages"]
        response = self.model.invoke(messages)
        # We return a list, because this will get added to the existing list
        return {"messages": [response]}

    # Define the function to execute tools
    def call_tool(self, state):
        messages = state["messages"]
        # Based on the continue condition
        # we know the last message involves a function call
        last_message = messages[-1]
        # We construct an ToolInvocation from the function_call
        action = ToolInvocation(
            tool=last_message.additional_kwargs["function_call"]["name"],
            tool_input=json.loads(
                last_message.additional_kwargs["function_call"]["arguments"]
            ),
        )
        # We call the tool_executor and get back a response
        response = self.tool_executor.invoke(action)
        # We use the response to create a FunctionMessage
        function_message = FunctionMessage(content=str(response), name=action.tool)
        # We return a list, because this will get added to the existing list
        return {"messages": [function_message]}

    def build_graph(self):
        workflow = StateGraph(AgentState)

        # Define the two nodes we will cycle between
        workflow.add_node("agent", self.call_model)
        workflow.add_node("action", self.call_tool)

        # Set the entrypoint as `agent` where we start
        workflow.set_entry_point("agent")

        # We now add a conditional edge
        workflow.add_conditional_edges(
            # First, we define the start node. We use `agent`.
            # This means these are the edges taken after the `agent` node is called.
            "agent",
            # Next, we pass in the function that will determine which node is called next.
            self.should_continue,
            # Finally we pass in a mapping.
            # The keys are strings, and the values are other nodes.
            # END is a special node marking that the graph should finish.
            # What will happen is we will call `should_continue`, and then the output of that
            # will be matched against the keys in this mapping.
            # Based on which one it matches, that node will then be called.
            {
                # If `tools`, then we call the tool node.
                "continue": "action",
                # Otherwise we finish.
                "end": END,
            },
        )

        # We now add a normal edge from `tools` to `agent`.
        # This means that after `tools` is called, `agent` node is called next.
        workflow.add_edge("action", "agent")

        # Finally, we compile it!
        # This compiles it into a LangChain Runnable,
        # meaning you can use it as you would any other runnable
        self.graph = workflow.compile()

    def invoke(self, query: str):
        user_message = HumanMessage(content=query)
        self.state["messages"].append(user_message)

        state = self.graph.invoke(self.state)
        response = state["messages"][-1]
        # self.state["messages"].append(response)

        return response.content


SYSTEM_PROMPT = """
You are a helpful hotel reservations assistant.
Your job is to help users book hotel rooms.
You should always ask the user for the information needed to make the reservation, don't guess it.
"""
