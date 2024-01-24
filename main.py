import logging

from bdd_llm.llm_user import DUMB_USER, NORMAL_USER_PROMPT, LLMUser
from bdd_llm.runners import UserConversation
from bdd_llm.user import ConsoleUser, DeterministicUser
from hotel_reservations.assistant import HotelReservationsAssistant
from hotel_reservations.core import make_reservation

logging.basicConfig(
    level=logging.WARNING,
)


def start():
    query = "I want to book a room in Paris for the next weekend, for me and my wife"
    metadata = {
        "name": "Pedro Sousa",
    }
    user = ConsoleUser()
    user = DeterministicUser(
        [
            query,
            "2",
            "bye",
        ]
    )
    user = LLMUser(NORMAL_USER_PROMPT, query, metadata)

    assistant = HotelReservationsAssistant(verbose=True)

    conversation = UserConversation(
        user=user,
        assistant=lambda query: assistant.invoke(query),
        max_iterations=3,
    )
    conversation.start_conversation(query)

    for log in conversation.chat_log:
        print(log)


if __name__ == "__main__":
    start()
