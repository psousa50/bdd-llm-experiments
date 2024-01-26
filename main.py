import logging


from bdd_llm.llm_user import LLMUser
from bdd_llm.mocks import create_mock
from bdd_llm.runners import UserConversation
from hotel_reservations.assistant import HotelReservationsAssistant
from hotel_reservations.core import make_reservation
from hotel_reservations.dependencies import HotelReservationsAssistantDependencies


def start():
    goal = "Book a room in in an Hotel in London, for 3 days, starting tomorrow, for two guests Price should be less than 20"  # noqa E501
    metadata = {
        "name": "Pedro Sousa",
    }
    persona = """
    You're a helpful user who tries to answer the LLM's questions as best as you can.
    """
    # persona = """
    # You're an arrogant user that sometimes get's fed up with the LLM's questions.
    # What you really want is to book a room in Hotel H3, in Paris, for 3 days, starting 12 Mar of 2024.
    # It's for five guests.
    # """
    # persona = """
    # You're a dumb user who tries to answer the LLM's questions as best as you can.
    # You cannot answer more than one question at a time.
    # Sometimes you don't understand the question and ask to repeat it.
    # """
    user = LLMUser(goal, persona, metadata)

    wrapped_make_reservation = create_mock(make_reservation)

    dependencies = HotelReservationsAssistantDependencies(
        make_reservation=wrapped_make_reservation,
    )
    assistant = HotelReservationsAssistant(dependencies, verbose=True)

    query = "I want to book a room"
    conversation = UserConversation(
        user=user,
        assistant=lambda query: assistant.invoke(query),
        stop_condition=lambda state: dependencies.make_reservation.called or bye(state),
        options={"verbose": True},
    )
    conversation.start_conversation(query)

    print(query)
    for log in conversation.chat_history:
        print(log)


def bye(state):
    return "bye" in state.chat_history[-1].message.lower()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start()
