from typing import Any

from langchain_core.messages import HumanMessage
from tests.llm_user import llm_user, llm_user_node

from hotel_reservations.assistant import hotel_reservations_assistant


def deterministic_user():
    m = -1
    messages = [
        "I want to book a room",
        "I want to book a room in London, starting in May 2 and ending in May 7, for 3 guests",
        "I want to book Hotel UK 2",
    ]

    def fn(_):
        nonlocal m
        m += 1
        return (
            HumanMessage(content=messages[m])
            if m < len(messages)
            else HumanMessage(content="FINISH")
        )

    return fn


def start():
    persona = "My name is Pedro Sousa and I want to book a room in London, starting in May 2 and ending in May 7, for 3 guests. I prefre UK 2"  # noqa E501
    user = llm_user_node(llm_user(persona))
    assistant = hotel_reservations_assistant(user=user)
    messages: Any = assistant.invoke([])
    for m in messages:
        print(m.content)


if __name__ == "__main__":
    start()
