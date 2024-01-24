import json
import logging

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_openai import ChatOpenAI

from bdd_llm.user import UserProxy

logger = logging.getLogger(__name__)


class LLMUser(UserProxy):
    def __init__(self, query, persona, metadata={}):
        self.agent = self.build_agent(query, persona, metadata)

    def get_input(self, question):
        logger.info(f"User question: {question}")
        response = self.agent.invoke({"input": question})
        logger.info(f"User response: {response}")
        return response

    def build_agent(self, query, persona, metadata):
        template = PromptTemplate.from_template(BASE_USER_PROMPT)
        system_prompt = template.format(
            query=query,
            persona=persona,
            metadata=json.dumps(metadata).replace("{", "").replace("}", ""),
        )

        logger.info(f"System Prompt: {system_prompt}")

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
    User your metadata to answer the questions. If you don't know the answer, just say "I don't know".

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
