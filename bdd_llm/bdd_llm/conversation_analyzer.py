from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from bdd_llm.messages import ChatMessage


class ConversationAnalyzer:
    def __init__(self):
        self.llm = self.build_llm()

    def invoke(self, conversation: list[ChatMessage]):
        query = "\n".join([message.content for message in conversation])
        response = self.llm.invoke({"input": query})
        return response

    def build_llm(self):
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.0,
        )
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", PROMPT),
                ("user", "{input}"),
            ]
        )

        chain = prompt | llm
        return chain


PROMPT = """
You are a conversational analyst. You are given a conversation between a user and an assistant.
Your task is to analyze the conversation to check if the assistant is answering the user's questions correctly.
Take special attention to the following points:
    - Dates are corectly handled and calculated.

Your response should be in JSON format using the following structure:
{{
    "score": <0..9>
    "feedback": "Your feedback here"
}}

Conversation:
{input}
"""
