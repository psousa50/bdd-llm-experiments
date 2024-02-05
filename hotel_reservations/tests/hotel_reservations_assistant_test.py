import datetime

from tests.helpers import create_test_conversation

from bdd_llm.llm_user import LLMUser
from hotel_reservations.core import Hotel

verbose = True


def test_query_with_all_the_information():
    # Given
    user = LLMUser.from_config(
        goal="Book a room in the Park Grand London Kensington hotel, for 3 days, starting 12 Feb, for two guests",  # noqa E501
        persona="A helpful user",
    )
    # When
    query = """
    Hi, my name is Pedro Sousa. I want to book a room in the Park Grand London Kensington hotel, for 3 days, starting 12 Feb. It's for two guests.
    """  # noqa E501
    conversation, dependencies = create_test_conversation(
        user,
        find_hotels_return_value=[
            Hotel(234, "Park Grand London Kensington", "London"),
        ],
    )
    conversation.start_conversation(query)

    for chat in conversation.state.chat_history:
        print(chat)

    # Then
    dependencies.make_reservation.assert_called_once_with(
        234,
        "Pedro Sousa",
        datetime.date(2024, 2, 12),
        datetime.date(2024, 2, 15),
        2,
    )


def test_query_with_all_the_information_full_prompt():
    # Given
    user = LLMUser.from_persona(
        persona="""My name is Pedro Sousa and I'm a helpful user.""",
    )
    # When
    query = """
    Hi, my name is Pedro Sousa. I want to book a room in the Park Grand London Kensington hotel, for 3 days, starting 12 Feb. It's for two guests.
    """  # noqa E501
    conversation, dependencies = create_test_conversation(
        user,
        find_hotels_return_value=[
            Hotel(234, "Park Grand London Kensington", "London"),
        ],
        options={"verbose": verbose},
    )
    conversation.start_conversation(query)

    # Then
    dependencies.make_reservation.assert_called_once_with(
        234,
        "Pedro Sousa",
        datetime.date(2024, 2, 12),
        datetime.date(2024, 2, 15),
        2,
    )


def test_query_with_relative_dates():
    # Given
    user = LLMUser.from_config(
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
    user = LLMUser.from_config(
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
    user = LLMUser.from_config(
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
        options={"verbose": True},
    )
    conversation.start_conversation(query)

    # Then
    dependencies.make_reservation.assert_called_once_with(
        3,
        "Pedro Sousa",
        datetime.date(2024, 2, 3),
        datetime.date(2024, 2, 6),
        2,
    )
