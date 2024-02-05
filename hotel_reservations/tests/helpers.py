import datetime
from typing import Callable, Union

from bdd_llm.mocks import create_mock
from bdd_llm.runners import UserConversation, UserConversationState
from hotel_reservations.assistant import HotelReservationsAssistant
from hotel_reservations.core import (
    calc_reservation_price,
    find_hotels,
    make_reservation,
)
from hotel_reservations.dependencies import (
    HotelReservationsAssistantDependencies,
    current_date,
)


def user_said_bye(state):
    return state.chat_history[-1].content.lower() == "bye"


def default_stop_condition(dependencies):
    def stop(state):
        return dependencies.make_reservation.called or user_said_bye(state)

    return stop


def create_dependencies(
    find_hotels_return_value=["H1", "H2", "H3"],
    calc_reservation_price_return_value=100,
    current_date_return_value=datetime.date(2024, 1, 1),
):
    dependencies = HotelReservationsAssistantDependencies(
        find_hotels=create_mock(find_hotels, return_value=find_hotels_return_value),
        calc_reservation_price=create_mock(
            calc_reservation_price, return_value=calc_reservation_price_return_value
        ),
        make_reservation=create_mock(make_reservation, return_value=True),
        current_date=create_mock(current_date, return_value=current_date_return_value),
    )
    return dependencies


def chat_fn(assistant):
    def fn(query: str) -> str:
        response = assistant.invoke(query)
        return response["output"]

    return fn


def create_test_conversation(
    user,
    find_hotels_return_value=["H1", "H2", "H3"],
    calc_reservation_price_return_value=100,
    current_date_return_value=datetime.date(1900, 1, 1),
    stop_condition: Union[Callable[[UserConversationState], bool], None] = None,
    max_iterations=10,
    options={},
):
    dependencies = create_dependencies(
        find_hotels_return_value=find_hotels_return_value,
        calc_reservation_price_return_value=calc_reservation_price_return_value,
        current_date_return_value=current_date_return_value,
    )
    assistant = HotelReservationsAssistant(
        dependencies, verbose=options.get("verbose", False)
    )

    if stop_condition is None:
        stop_condition = default_stop_condition(dependencies)
    conversation = UserConversation(
        user=user,
        assistant=chat_fn(assistant),
        stop_condition=stop_condition,
        max_iterations=max_iterations,
        options=options,
    )

    return conversation, dependencies
