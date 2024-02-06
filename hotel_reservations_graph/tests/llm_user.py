from typing import Union

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI


class LLMUserOptions:
    def __init__(
        self,
        model: str = "gpt-4",
        temperature: float = 0.0,
    ) -> None:
        self.model = model
        self.temperature = temperature


def default_llm(options: LLMUserOptions):
    return ChatOpenAI(model=options.model, temperature=options.temperature)


def llm_user(persona: str, options=LLMUserOptions(), llm=None):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", LLM_USER_PROMPT),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    prompt = prompt.partial(persona=persona)
    if llm is None:
        llm = default_llm(options)
    return prompt | llm


def _swap_roles(messages):
    new_messages = []
    for m in messages:
        if isinstance(m, AIMessage):
            new_messages.append(HumanMessage(content=m.content))
        else:
            new_messages.append(AIMessage(content=m.content))
    return new_messages


def llm_user_node(llm_user):
    def user(messages: list[BaseMessage]) -> Union[BaseMessage, list[BaseMessage]]:
        new_messages = _swap_roles(messages)
        return llm_user.invoke({"messages": new_messages})

    return user


LLM_USER_PROMPT = """
    Your role is to simulate a user that asked an Assistant to do a task. Remember, you are not the Assistant, you are the user.
    If you don't know the answer, just pick a random one.

    This is how you describe yourself and want you want to accomplish:
    {persona}

    When the LLM finishes the task, it will not ask a question, it will just give you the result.
    You should then responde only the word "FINISH" to end the conversation.

    """  # noqa E501
