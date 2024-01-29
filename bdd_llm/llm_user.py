import logging

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_openai import ChatOpenAI
from bdd_llm.callbacks import LLMStartHandler
from bdd_llm.messages import ChatMessage

from bdd_llm.user import UserProxy

logger = logging.getLogger(__name__)


class LLMUser(UserProxy):
    def __init__(self, goal: str, persona: str, metadata: dict = {}):
        self.agent = self.build_agent(goal, persona, metadata)

        self.handler = LLMStartHandler()

    def get_input(self, question: str, chat_history: list[ChatMessage]):
        logger.info(f"User question: {question}")
        formatted_chat_history = self.format_chat_history(chat_history)
        response = self.agent.invoke(
            {"input": question, "chat_history": formatted_chat_history},
            config={"callbacks": [self.handler]},
        )
        logger.info(f"User response: {response}")
        return response

    def build_agent(self, goal, persona, metadata):
        template = PromptTemplate.from_template(BASE_USER_PROMPT)
        system_prompt = template.format(
            goal=goal,
            persona=persona,
            metadata=self.format_metadata(metadata),
        )

        logger.info(f"System Prompt: {system_prompt}")

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("user", "{input}"),
            ]
        )
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.0,
        )
        output_parser = StrOutputParser()
        chain = prompt | llm | output_parser
        return chain

    def format_metadata(self, metadata):
        return "\n".join([f"{k}: {v}" for k, v in metadata.items()])

    def format_chat_history(self, chat_history: list[ChatMessage]):
        return "\n".join([repr(m) for m in chat_history])


BASE_USER_PROMPT = """
    Your role is to simulate a user that asked an LLM to do a task. Remember, you are not the LLM, you are the user.
    If you don't know the answer, just say "I don't know".

    Here is some information about you:
    {metadata}
    =============================

    Here is your goal
    {goal}
    =============================

    This is how you should behave:
    {persona}
    =============================

    This is the chat history:
    {{chat_history}}
    =============================

    When the LLM finishes the task, it will not ask a question, it will just give you the result.
    You should then say "bye" to the LLM to end the conversation.

    Here is the LLM Question:

    {{input}}
    """
