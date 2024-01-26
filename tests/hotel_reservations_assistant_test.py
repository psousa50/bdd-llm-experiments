import datetime
from typing import Callable

from bdd_llm.llm_user import LLMUser
from bdd_llm.mocks import create_mock
from bdd_llm.runners import UserConversation, UserConversationState
from hotel_reservations.assistant import HotelReservationsAssistant
from hotel_reservations.core import (
    Hotel,
    calc_reservation_price,
    find_hotels,
    make_reservation,
)
from hotel_reservations.dependencies import (
    HotelReservationsAssistantDependencies,
    current_date,
    current_year,
)


def user_said_bye(state):
    return state.chat_history[-1].message.lower() == "bye"


def default_stop_condition(dependencies):
    def stop(state):
        return dependencies.make_reservation.called or user_said_bye(state)

    return stop


def create_dependencies(
    find_hotels_return_value=["H1", "H2", "H3"],
    calc_reservation_price_return_value=100,
    current_date_return_value=datetime.date(2024, 1, 1),
    current_year_return_value=1900,
):
    dependencies = HotelReservationsAssistantDependencies(
        find_hotels=create_mock(find_hotels, return_value=find_hotels_return_value),
        calc_reservation_price=create_mock(
            calc_reservation_price, return_value=calc_reservation_price_return_value
        ),
        make_reservation=create_mock(make_reservation, return_value=True),
        current_date=create_mock(current_date, return_value=current_date_return_value),
        current_year=create_mock(current_year, return_value=current_year_return_value),
    )
    return dependencies


def create_test_conversation(
    user,
    find_hotels_return_value=["H1", "H2", "H3"],
    calc_reservation_price_return_value=100,
    current_date_return_value=datetime.date(1900, 1, 1),
    current_year_return_value=1900,
    stop_condition: Callable[[UserConversationState], bool] = None,
    max_iterations=10,
    options={},
):
    dependencies = create_dependencies(
        find_hotels_return_value=find_hotels_return_value,
        calc_reservation_price_return_value=calc_reservation_price_return_value,
        current_date_return_value=current_date_return_value,
        current_year_return_value=current_year_return_value,
    )
    assistant = HotelReservationsAssistant(dependencies)

    if stop_condition is None:
        stop_condition = default_stop_condition(dependencies)
    conversation = UserConversation(
        user=user,
        assistant=lambda query: assistant.invoke(query),
        stop_condition=stop_condition,
        max_iterations=max_iterations,
        options=options,
    )

    return conversation, dependencies


def test_query_with_all_the_information():
    # Given
    user = LLMUser(
        goal="Book a room in the Park Grand London Kensington hotel, for 3 days, starting 12 Feb of 2024, for two guests",  # noqa E501
        persona="A helpful user",
    )
    # When
    query = """
    Hi, my name is Pedro Sousa. I want to book a room in the Park Grand London Kensington hotel, for 3 days, starting 12 Feb of 2024. It's for two guests.
    """  # noqa E501
    conversation, dependencies = create_test_conversation(
        user,
        find_hotels_return_value=[
            Hotel(234, "Park Grand London Kensington", "London"),
        ],
        current_year_return_value=2024,
    )
    conversation.start_conversation(query)

    # Then
    dependencies.current_year.assert_called_once()
    dependencies.make_reservation.assert_called_once_with(
        234,
        "Pedro Sousa",
        datetime.date(2024, 2, 12),
        datetime.date(2024, 2, 15),
        2,
    )


def test_query_with_relative_dates():
    # Given
    user = LLMUser(
        goal="Book a room in the Britannia International Hotel, for the next weekend, starting Friday, for me, my wife and our two kids",  # noqa E501
        persona="A helpful user",
        metadata={
            "name": "Pedro Sousa",
        },
    )
    # When
    query = """
    I want to book a room In London.
    """
    conversation, dependencies = create_test_conversation(
        user,
        find_hotels_return_value=[
            Hotel(1, "Britannia International Hotel", "London"),
            Hotel(2, "Park Grand London Kensington", "London"),
            Hotel(3, "Park Plaza Westminster Bridge London", "London"),
        ],
        current_date_return_value=datetime.date(2024, 1, 23),
        current_year_return_value=2024,
    )
    conversation.start_conversation(query)

    # Then
    dependencies.current_date.assert_called_once()
    dependencies.make_reservation.assert_called_once_with(
        1,
        "Pedro Sousa",
        datetime.date(2024, 1, 26),
        datetime.date(2024, 1, 28),
        4,
    )


def test_query_with_no_information():
    # Given
    user = LLMUser(
        goal="Book a room in a London Hotel, starting in 3 of February, for 3 days, for two guests. I prefer hotel UK 2",  # noqa E501
        persona="A helpful user",
        metadata={
            "name": "Pedro Sousa",
        },
    )

    # When
    query = "I want to book a room"
    conversation, dependencies = create_test_conversation(
        user,
        find_hotels_return_value=[
            Hotel(2, "Hotel UK 2", "London"),
        ],
        current_year_return_value=2027,
        options={"verbose": True},
    )
    conversation.start_conversation(query)

    # Then
    dependencies.current_date.assert_not_called()
    dependencies.find_hotels.assert_called_once_with(name="UK 2", location="London")
    dependencies.make_reservation.assert_called_once_with(
        2,
        "Pedro Sousa",
        datetime.date(2027, 2, 3),
        datetime.date(2027, 2, 6),
        2,
    )


def test_slow_user_with_no_information():
    # Given
    user = LLMUser(
        goal="Book a room in a London Hotel, starting in 3 of February, for 3 days, for two guests. I think the hotel anme is Plaza something",  # noqa E501
        persona="A slow user that cannot answer more than one question at a time",
        metadata={
            "name": "Pedro Sousa",
        },
    )

    # When
    query = "I want to book a room"
    conversation, dependencies = create_test_conversation(
        user,
        find_hotels_return_value=[
            Hotel(1, "Britannia International Hotel", "London"),
            Hotel(2, "Park Grand London Kensington", "London"),
            Hotel(3, "Park Plaza Westminster Bridge London", "London"),
        ],
        current_year_return_value=2024,
        options={"verbose": True},
    )
    conversation.start_conversation(query)

    # Then
    dependencies.current_year.assert_called_once()
    dependencies.make_reservation.assert_called_once_with(
        3,
        "Pedro Sousa",
        datetime.date(2024, 2, 3),
        datetime.date(2024, 2, 6),
        2,
    )
