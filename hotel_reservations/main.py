import json
import logging
from datetime import datetime

from bdd_llm.conversation_analyzer import ConversationAnalyzer
from bdd_llm.llm_user import LLMUser
from bdd_llm.mocks import create_mock
from bdd_llm.runners import UserConversation
from hotel_reservations.assistant import HotelReservationsAssistant
from hotel_reservations.core import make_reservation
from hotel_reservations.dependencies import HotelReservationsAssistantDependencies

verbose = False


def filter(record):
    print("record.name:", record.name)
    return record.name in ["hotel_reservations.callbacks"]


def start():
    user = LLMUser.from_persona(
        persona="""
        My name is Pedro Sousa and I'm a helpful user.
        I want to book a room in London, starting in May 2 and ending in May 7
        It will be for 4 guests
        """,  # noqa E501
    )

    wrapped_make_reservation = create_mock(make_reservation)

    dependencies = HotelReservationsAssistantDependencies(
        make_reservation=wrapped_make_reservation,
        current_date=lambda: datetime(2024, 1, 23),
    )
    assistant = HotelReservationsAssistant(dependencies, verbose=verbose)

    query = "I want to book a room"
    conversation = UserConversation(
        user=user,
        assistant=lambda query: assistant.invoke(query),
        stop_condition=lambda state: dependencies.make_reservation.called or bye(state),
        options={"verbose": verbose},
    )
    conversation.start_conversation(query)

    print(user.persona)
    print()
    print(query)
    for log in conversation.state.chat_history:
        print(log)

    conversationAnalyzer = ConversationAnalyzer()
    response = conversationAnalyzer.invoke(conversation.state.chat_history)
    response_json = json.loads(response.content)
    print(response_json)


def bye(state):
    return "bye" in state.chat_history[-1].message.lower()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for handler in logging.root.handlers:
        handler.addFilter(filter)
    start()
