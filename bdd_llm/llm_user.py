import json

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from bdd_llm.log import Log

from bdd_llm.user import UserProxy


class LLMUser(UserProxy):
    def __init__(self, system_prompt, query, metadata={}):
        self.system_prompt = system_prompt
        self.query = query
        self.metadata = metadata
        self.log = Log("LLMUser")

        self.agent = self.build_agent(query, metadata)

    def get_input(self, question):
        self.log("User question", question)
        response = self.agent.invoke({"input": question})
        self.log("User response", response)
        return response

    def build_agent(self, query, user_metadata: dict = {}):
        system_prompt = self.system_prompt.format(
            query=query,
            metadata=json.dumps(user_metadata).replace("{", "").replace("}", ""),
        )

        self.log("System Prompt", system_prompt)

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("user", "{input}"),
            ]
        )

        model = ChatOpenAI(model="gpt-4", temperature=0.0)
        output_parser = StrOutputParser()

        chain = prompt | model | output_parser

        return chain


BASE_USER_PROMPT = """
    Your role is to simulate a user that asked an LLM to do a task. Remember, you are not the LLM, you are the user.

    Here is some information about you:
    {metadata}

    This is how you should behave:    
    {persona}
    
    This is the task that you asked the LLM to do:
    {query}
    
    When the LLM finishes the task, it will not ask a question, it will just give you the result.
    You should then say "bye" to the LLM to end the conversation.
    
    Here is the LLM Question:

    {{input}}
    """

NORMAL_USER = "NORMAL_USER"
NORMAL_USER_PERSONA = """
    Sometimes the LLM assistant needs to ask you a question to be able to complete the task. Please answer the question.
    If the question is about making a choice, choose a ramdom option.
"""

DUMB_USER = "DUMB_USER"
DUMB_USER_PERSONA = """
    Sometimes the LLM assistant needs to ask you a question to be able to complete the task.
    You should always answer "I don't know" to the question.
"""

NORMAL_USER_PROMPT = BASE_USER_PROMPT.replace("{persona}", NORMAL_USER_PERSONA)
DUMB_USER_PROMPT = BASE_USER_PROMPT.replace("{persona}", DUMB_USER_PERSONA)
