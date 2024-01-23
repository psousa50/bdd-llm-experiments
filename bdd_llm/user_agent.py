import json

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_openai import ChatOpenAI


def build_agent(query, user_metadata: dict = {}):
    DEFAULT_SYSTEM_PROMPT = """
    Your role is to simulate a user that asked an LLM to do a task.
    
    This is the task that you asked the LLM to do:
    {query}

    Sometimes the LLM assistant needs to ask you a question to be able to complete the task. Please answer the question.
    If the question is about making a choice, choose a ramdom option.
    
    Here is some information about you:
    {metadata}

    When the LLM finishes the task, it will not ask a question, it will just give you the result.
    You should then say "bye" to the LLM to end the conversation.
    
    Here is the LLM Question:

    {{input}}
    """

    system_prompt = DEFAULT_SYSTEM_PROMPT.format(
        query=query,
        metadata=json.dumps(user_metadata).replace("{", "").replace("}", ""),
    )
    print("system_prompt", system_prompt)

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
