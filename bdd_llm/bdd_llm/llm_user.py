import logging

from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
)
from langchain_openai import ChatOpenAI

from bdd_llm.callbacks import LLMStartHandler
from bdd_llm.user import UserProxy

logger = logging.getLogger(__name__)


def default_llm():
    return ChatOpenAI(
        model="gpt-4",
        temperature=0.0,
    )


class LLMUser(UserProxy):
    @classmethod
    def from_parts(
        cls, llm: BaseLanguageModel, goal: str, persona: str, metadata: dict = {}
    ):
        prompt = LLMUser.build_persona_prompt(goal, persona, metadata)
        return cls(prompt, llm)

    @classmethod
    def from_persona(cls, persona: str, llm=None):
        return cls(persona, llm)

    @staticmethod
    def build_persona_prompt(goal, persona, metadata):
        persona_template = PromptTemplate.from_template(FROM_PARTS_PROMPT)
        return persona_template.format(
            metadata=LLMUser.format_metadata(metadata),
            goal=goal,
            persona=persona,
        )

    @staticmethod
    def format_metadata(metadata):
        return "\n".join([f"{k}: {v}" for k, v in metadata.items()])

    def __init__(self, persona, llm):
        template = PromptTemplate.from_template(BASE_USER_PROMPT)
        prompt = template.format(persona=persona)
        self.persona = persona
        self.agent = self.build_agent(prompt, llm)
        self.handler = LLMStartHandler()
        self.chat_history = []

    def get_input(self, query: str):
        response = self.agent.invoke(
            {"input": query, "chat_history": self.chat_history},
            config={"callbacks": [self.handler]},
        )
        # print(f"type(response): {type(response)}")
        # print(f"response: {response}")
        self.chat_history.append(HumanMessage(content=query))
        self.chat_history.append(AIMessage(content=response))
        return response

    def build_agent(self, prompt, llm):
        logger.info(f"LLMUser Prompt: {prompt}")

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
            ]
        )
        output_parser = StrOutputParser()
        chain = prompt | llm | output_parser
        return chain


BASE_USER_PROMPT = """
    Your role is to simulate a user that asked an Assistant to do a task. Remember, you are not the Assistant, you are the user.
    If you don't know the answer, just pick a random one.

    Here is some information about you:
    {persona}

    When the LLM finishes the task, it will not ask a question, it will just give you the result.
    You should then say "bye" to the LLM to end the conversation.

    Conversation:
    {{chat_history}}
    -------------
    """  # noqa E501

PERSONA_PROMPT = """
    This is how you should behave:
    {persona}
    -------------
    """

FROM_PARTS_PROMPT = """
    Here is some information about you:
    {metadata}
    -------------

    Here is your goal:
    {goal}
    -------------

    This is how you should behave:
    {persona}
    -------------
    """
