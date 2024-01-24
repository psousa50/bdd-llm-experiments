import datetime


from bdd_llm.llm_user import NORMAL_USER_PROMPT, LLMUser
from bdd_llm.log import Log
from bdd_llm.mocks import create_mock
from bdd_llm.runners import UserConversation
from hotel_reservations.assistant import HotelReservationsAssistant
from hotel_reservations.core import find_hotels, make_reservation
from hotel_reservations.dependencies import (
    HotelReservationsAssistantDependencies,
    current_date,
)

Log.set_verbose(False)


def test__query_with_all_the_information():
    ## Given
    metadata = {
        "name": "Pedro Sousa",
    }
    query = "My name is Pedro Sousa. I want to book a room in Hotel Palace, for 3 days, starting 12 Feb of 2024. It's for two guests"
    llmUser = LLMUser(NORMAL_USER_PROMPT, query, metadata)

    dependencies = HotelReservationsAssistantDependencies(
        find_hotels=create_mock(find_hotels, return_value=["H1", "H2", "H3"]),
        make_reservation=create_mock(make_reservation),
        current_date=create_mock(current_date),
    )
    assistant = HotelReservationsAssistant(dependencies)

    ## When
    conversation = UserConversation(
        user=llmUser,
        assistant=lambda query: assistant.invoke(query),
        stop_condition=lambda: dependencies.make_reservation.called,
        max_iterations=5,
    )
    conversation.start_conversation(query)

    ## Then
    dependencies.make_reservation.assert_called_once_with(
        "Hotel Palace",
        "Pedro Sousa",
        datetime.date(2024, 2, 12),
        datetime.date(2024, 2, 15),
        2,
    )
