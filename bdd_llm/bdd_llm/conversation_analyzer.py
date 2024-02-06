from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI


class ConversationAnalyzer:
    def __init__(self):
        self.llm = self.build_llm()

    def invoke(self, chat_history: list[BaseMessage]):
        response = self.llm.invoke({"chat_history": chat_history})
        return response

    def build_llm(self):
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.0,
        )
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", PROMPT),
                MessagesPlaceholder(variable_name="chat_history"),
            ]
        )

        chain = prompt | llm | JsonOutputParser()
        return chain


PROMPT = """
You are a conversational analyst. You are given a conversation between a user and an assistant.
Your task is to analyze the conversation to check if the assistant is answering the user's questions correctly.

Your response should be in JSON format using the following structure:
{{
    "score": <0..9>
    "feedback": "Your feedback here"
}}

Conversation:
{chat_history}
"""
