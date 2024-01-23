import datetime
from unittest.mock import Mock

from bdd_llm.user import ConsoleUser, DeterministicUser, RegularUser, stop_condition
from hotel_reservations.assistant import HotelReservationsAssistant
from hotel_reservations.core import make_reservation


def test_chat_assistant():
    ## Given
    metadata = {
        "name": "Pedro Sousa",
    }
    query = "My name is Pedro Sousa. I want to book a room in London, for 3 days, starting 12 Feb of 2024. It's for two guests"
    user = ConsoleUser()
    user = DeterministicUser(
        [
            query,
            "2",
            "bye",
        ]
    )
    user = RegularUser(query, metadata)
    make_reservation_mock = Mock(wraps=make_reservation)
    assistant = HotelReservationsAssistant(
        user_proxy=user,
        make_reservation=make_reservation_mock,
        stop_condition=stop_condition,
    )

    ## When
    assistant.start()

    ## Then
    print("make_reservation_mock.call_args", make_reservation_mock.call_args)
    make_reservation_mock.assert_called_once_with(
        "Hotel UK 2",
        "Pedro Sousa",
        datetime.date(2024, 2, 12),
        datetime.date(2024, 2, 15),
        2,
    )
