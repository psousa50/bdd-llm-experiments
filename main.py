from bdd_llm.llm_user import LLMUser
from bdd_llm.mocks import create_mock
from bdd_llm.runners import UserConversation
from hotel_reservations.assistant import HotelReservationsAssistant
from hotel_reservations.core import make_reservation
from hotel_reservations.dependencies import HotelReservationsAssistantDependencies


def start():
    query = "I want to book a room"
    metadata = {
        "name": "Pedro Sousa",
    }
    persona = """
    You're a helpful user who tries to answer the LLM's questions as best as you can.
    When asked about the location, you say "Paris".
    When asked about the hotel, you say "H3".
    When asked about the checkin and checkout dates, you say "12 Mar 2024, 15 Mar 2024".
    When asked about the number of guests, you say "3".
    """
    persona = """
    You're an arrogant user that sometimes get's fed up with the LLM's questions.
    What you really want is to book a room in Hotel H3, in Paris, for 3 days, starting 12 Mar of 2024. It's for five guests.
    """
    persona = """
    You're a dumb user who tries to answer the LLM's questions as best as you can.
    What you really want is to book a room in Hotel H3, in Paris, for 3 days, starting 12 Mar of 2024. It's for five guests.
    You cannot answer more than one question at a time.
    Sometimes you forget what you want and need time to think.
    """
    user = LLMUser(query, persona, metadata)

    wrapped_make_reservation = create_mock(make_reservation)

    dependencies = HotelReservationsAssistantDependencies(
        make_reservation=wrapped_make_reservation,
    )
    assistant = HotelReservationsAssistant(dependencies, verbose=True)

    conversation = UserConversation(
        user=user,
        assistant=lambda query: assistant.invoke(query),
        stop_condition=lambda: dependencies.make_reservation.called,
    )
    conversation.start_conversation(query)

    print(query)
    for log in conversation.chat_log:
        print(log)


if __name__ == "__main__":
    start()
