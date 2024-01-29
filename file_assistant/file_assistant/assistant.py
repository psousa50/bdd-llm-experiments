import logging

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain_community.tools.file_management import (
    ReadFileTool,
    WriteFileTool,
    ListDirectoryTool,
)
from langchain_community.agent_toolkits import FileManagementToolkit

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)

working_directory = "tmp/"


class FileAssistantDependencies:
    def __init__(
        self, read_file=None, write_file=None, list_directory=None, root_dir="tmp"
    ) -> None:
        tools = FileManagementToolkit(
            root_dir=str(root_dir),
            selected_tools=["read_file", "write_file", "list_directory"],
        ).get_tools()
        if read_file is None:
            read_file = self.get_tool(tools, "ReadFileTool")
        if write_file is None:
            write_file = self.get_tool(tools, "WriteFileTool")
        if list_directory is None:
            list_directory = self.get_tool(tools, "ListDirectoryTool")
        self.read_file = read_file
        self.write_file = write_file
        self.list_directory = list_directory

    def get_tool(self, tools, tool_name):
        return [t for t in tools if type(t).__name__ == tool_name][0]


class FileAssistant:
    def __init__(
        self,
        dependencies=FileAssistantDependencies(),
        verbose=False,
    ):
        self.dependencies = dependencies
        self.verbose = verbose

        self.agent = self.build_agent()
        self.chat_history = []

    def build_agent(
        self,
    ):
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.0,
            openai_api_base="http://localhost:8000",
        )
        tools = [
            self.dependencies.read_file,
            self.dependencies.write_file,
            self.dependencies.list_directory,
        ]
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
        agent = create_openai_functions_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            return_intermediate_steps=True,
            verbose=self.verbose,
        )

        return agent_executor

    def invoke(self, query: str, session_id: str = "foo"):
        response = self.agent.invoke(
            {"input": query, "chat_history": self.chat_history},
            config={
                "configurable": {"session_id": session_id},
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


SYSTEM_PROMPT = """
You are a powerful assistant that can read, write, and list files.
"""
