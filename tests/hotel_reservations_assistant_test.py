import datetime

from bdd_llm.llm_user import LLMUser

from bdd_llm.mocks import create_mock
from bdd_llm.runners import UserConversation
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
)


def user_said_bye(state):
    return state.chat_history[-1].message.lower() == "bye"


def stop_condition(dependencies):
    def stop(state):
        return dependencies.make_reservation.called or user_said_bye(state)

    return stop


def create_test_conversation(
    user,
    find_hotels_return_value=["H1", "H2", "H3"],
    calc_reservation_price_return_value=100,
    current_date_return_value=datetime.date(2024, 1, 1),
    max_iterations=10,
    options={},
):
    dependencies = HotelReservationsAssistantDependencies(
        find_hotels=create_mock(find_hotels, return_value=find_hotels_return_value),
        calc_reservation_price=create_mock(
            calc_reservation_price, return_value=calc_reservation_price_return_value
        ),
        make_reservation=create_mock(make_reservation, return_value=True),
        current_date=create_mock(current_date, return_value=current_date_return_value),
    )
    assistant = HotelReservationsAssistant(dependencies, verbose=True)

    conversation = UserConversation(
        user=user,
        assistant=lambda query: assistant.invoke(query),
        stop_condition=stop_condition(dependencies),
        max_iterations=max_iterations,
        options=options,
    )

    return conversation, dependencies


def test_query_with_all_the_information():
    # Given
    user = LLMUser(
        goal="Book a room in Hotel Palace, for 3 days, starting 12 Feb of 2024, for two guests",
        persona="A helpful user",
        metadata={
            "name": "Pedro Sousa",
        },
    )
    # When
    query = """
    Hi, my name is Pedro Sousa. I want to book a room in Hotel Palace, for 3 days, starting 12 Feb of 2024.
    It's for two guests
    """
    conversation, dependencies = create_test_conversation(user)
    conversation.start_conversation(query)

    # Then
    dependencies.find_hotels.assert_not_called()
    dependencies.current_date.assert_not_called()
    dependencies.make_reservation.assert_called_once_with(
        "Hotel Palace",
        "Pedro Sousa",
        datetime.date(2024, 2, 12),
        datetime.date(2024, 2, 15),
        2,
    )


def test_query_with_no_information():
    # Given
    user = LLMUser(
        goal="Book a room in a London Hotel, starting in 3 of February, for 3 days, for two guests. I prefer hotel UK 2",
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
            Hotel(1, "Hotel UK 1", "London"),
            Hotel(2, "Hotel UK 2", "London"),
            Hotel(3, "Hotel France 1", "Paris"),
        ],
        current_date_return_value=datetime.date(2021, 1, 1),
        options={"verbose": True},
    )
    conversation.start_conversation(query)

    # Then
    dependencies.make_reservation.assert_called_once_with(
        2,
        "Pedro Sousa",
        datetime.date(2021, 2, 3),
        datetime.date(2021, 2, 6),
        2,
    )


def test_too_pricey():
    # Given
    user = LLMUser(
        goal="Book a room in hotel H2, starting tomorrow, for 3 days. It's for two guests. Price should be less than 200",  # noqa E501
        persona="A helpful user but I'm very tight-fisted, I will not pay more than 200. I will give up if I can't find a hotel for that price",  # noqa E501
        metadata={
            "name": "Pedro Sousa",
        },
    )

    # When
    query = "I want to book a room in London starting on 12 Feb of 2024 for 3 days, for two guests. Price should be less than 200"  # noqa E501
    conversation, dependencies = create_test_conversation(
        user,
        find_hotels_return_value=["H1", "H2"],
        calc_reservation_price_return_value=300,
        options={"verbose": True},
    )
    conversation.start_conversation(query)

    # Then
    dependencies.make_reservation.assert_not_called()
    dependencies.find_hotels.assert_called_once_with("London")
    dependencies.calc_reservation_price.assert_any_call(
        "H1", datetime.date(2024, 2, 12), datetime.date(2024, 2, 15), 2
    )
    dependencies.calc_reservation_price.assert_any_call(
        "H2", datetime.date(2024, 2, 12), datetime.date(2024, 2, 15), 2
    )
    assert dependencies.calc_reservation_price.call_count == 2


# def test_should_give_up():
#     # Given
#     query = "My name is Pedro Sousa. I want to book a room in Hotel Palace, for 3 days, starting 12 Feb of 2024"
#     metadata = {
#         "name": "Pedro Sousa",
#     }
#     persona = """
#     You're a dumb user who always answers the LLM's questions with "I don't know".
#     """
#     user = LLMUser(query, persona, metadata)

#     # When
#     conversation, dependencies = create_test_conversation(
#         user,
#         find_hotels_return_value=["H1", "H2", "H3"],
#         max_iterations=2,
#     )
#     conversation.start_conversation(query)

#     # Then
#     dependencies.make_reservation.assert_not_called()


# def test_figure_it_out():
#     # Given
#     query = """
#     I want to book a room
#     """
#     metadata = {
#         "name": "Pedro Sousa",
#     }
#     persona = """
#     You're a nice and helpful user who tries to answer the LLM's questions as best as you can.
#     This is some information about you:

#     My name is Pedro Sousa.
#     I want to book a room in London, for 3 days, starting tomorrow.
#     The hotel name is Plaza something...
#     It will be for my wife and our two kids.

#     """
#     user = LLMUser(query, persona, metadata)

#     # When
#     conversation, dependencies = create_test_conversation(
#         user,
#         find_hotels_return_value=[
#             "Britannia International Hotel",
#             "Park Grand London Kensington",
#             "Park Plaza Westminster Bridge London",
#         ],
#         current_date_return_value=datetime.date(2021, 1, 1),
#     )
#     conversation.start_conversation(query)

#     print(query)
#     for log in conversation.chat_log:
#         print(log)

#     # Then
#     dependencies.find_hotels.assert_called_once_with("London")

#     dependencies.current_date.assert_called_once()

#     dependencies.make_reservation.assert_called_once_with(
#         "Park Plaza Westminster Bridge London",
#         "Pedro Sousa",
#         datetime.date(2021, 1, 2),
#         datetime.date(2021, 1, 5),
#         4,
#     )


def test():
    # Given
    user = LLMUser(
        goal="Book a room in hotel H3 in London, starting at tomorrow, for 3 days, for 2 guests",
        persona="I'm a dumb user so I can only answer one quick question at a time",
        metadata={
            "name": "Pedro Sousa",
        },
    )

    # When
    query = "I want to book a room"
    conversation, dependencies = create_test_conversation(
        user,
        find_hotels_return_value=["H1", "H2", "H3"],
        current_date_return_value=datetime.date(2022, 1, 1),
    )
    conversation.start_conversation(query)

    # Then
    dependencies.make_reservation.assert_called_once_with(
        "H3",
        "Pedro Sousa",
        datetime.date(2021, 1, 2),
        datetime.date(2021, 1, 5),
        2,
    )
