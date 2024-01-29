# import logging


from bdd_llm.llm_user import LLMUser
from bdd_llm.mocks import create_mock
from bdd_llm.runners import UserConversation
from hotel_reservations.assistant import HotelReservationsAssistant
from hotel_reservations.core import make_reservation
from hotel_reservations.dependencies import HotelReservationsAssistantDependencies


def start():
    user = LLMUser(
        goal="Book a room in a London Hotel, starting in 3 of February, for 3 days, for two guests. I prefer hotel UK 2",  # noqa E501
        persona="A helpful user",
        metadata={
            "name": "Pedro Sousa",
        },
    )

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
    # logging.basicConfig(level=logging.INFO)
    start()
