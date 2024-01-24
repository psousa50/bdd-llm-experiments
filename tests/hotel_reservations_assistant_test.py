import datetime

from bdd_llm.llm_user import LLMUser

from bdd_llm.mocks import create_mock
from bdd_llm.runners import UserConversation
from bdd_llm.user import DeterministicUser
from hotel_reservations.assistant import HotelReservationsAssistant
from hotel_reservations.core import find_hotels, make_reservation
from hotel_reservations.dependencies import (
    HotelReservationsAssistantDependencies,
    current_date,
)


def create_test_conversation(
    user,
    find_hotels_return_value=["H1", "H2", "H3"],
    max_iterations=20,
):
    dependencies = HotelReservationsAssistantDependencies(
        find_hotels=create_mock(find_hotels, return_value=find_hotels_return_value),
        make_reservation=create_mock(make_reservation),
        current_date=create_mock(current_date),
    )
    assistant = HotelReservationsAssistant(dependencies)

    conversation = UserConversation(
        user=user,
        assistant=lambda query: assistant.invoke(query),
        stop_condition=lambda: dependencies.make_reservation.called,
        max_iterations=max_iterations,
    )

    return conversation, dependencies


def test_query_with_all_the_information():
    # Given
    query = """My name is Pedro Sousa.
    I want to book a room in Hotel Palace, for 3 days, starting 12 Feb of 2024.
    It's for two guests
    """
    user = DeterministicUser(
        [
            query,
        ]
    )
    # When
    conversation, dependencies = create_test_conversation(user)
    conversation.start_conversation(query)

    # Then
    dependencies.make_reservation.assert_called_once_with(
        "Hotel Palace",
        "Pedro Sousa",
        datetime.date(2024, 2, 12),
        datetime.date(2024, 2, 15),
        2,
    )


def test_query_with_no_information():
    # Given
    query = "I want to book a room"
    metadata = {
        "name": "Pedro Sousa",
    }
    persona = """
    You're a dumb user who tries to answer the LLM's questions as best as you can.
    What you really want is to book a room in Hotel H3, in Paris, for 3 days, starting 12 Mar of 2024.
    It's for five guests.
    You cannot answer more than one question at a time.
    Sometimes you forget what you want and need time to think.
    """
    user = LLMUser(query, persona, metadata)

    # When
    conversation, dependencies = create_test_conversation(
        user, find_hotels_return_value=["H1", "H2", "H3"]
    )
    conversation.start_conversation(query)

    # Then
    dependencies.find_hotels.assert_called_once_with("Paris")

    dependencies.make_reservation.assert_called_once_with(
        "H3",
        "Pedro Sousa",
        datetime.date(2024, 3, 12),
        datetime.date(2024, 3, 15),
        5,
    )


def test_should_give_up():
    # Given
    query = "My name is Pedro Sousa. I want to book a room in Hotel Palace, for 3 days, starting 12 Feb of 2024"
    metadata = {
        "name": "Pedro Sousa",
    }
    persona = """
    You're a dumb user who alwyas answers the LLM's questions with "I don't know".
    """
    user = LLMUser(query, persona, metadata)

    # When
    conversation, dependencies = create_test_conversation(
        user,
        find_hotels_return_value=["H1", "H2", "H3"],
        max_iterations=2,
    )
    conversation.start_conversation(query)

    # Then
    dependencies.make_reservation.assert_not_called()
