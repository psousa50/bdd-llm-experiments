import datetime
import os

from bdd_llm.llm_user import LLMUser
from bdd_llm.mocks import create_mock
from bdd_llm.runners import UserConversation
from hotel_reservations.assistant import (
    HotelReservationsAssistant,
    HotelReservationsAssistantDependencies,
)
from hotel_reservations.core import Hotel, find_hotels, make_reservation

os.environ["LANGCHAIN_PROJECT"] = "Hotel Reservations Graph"


def user_said_bye(state):
    return state.chat_history[-1].message.lower() == "bye"


def stop_condition(dependencies):
    def stop(state):
        return dependencies.make_reservation.called or user_said_bye(state)

    return stop


def chat_fn(assistant):
    def fn(query: str) -> str:
        response = assistant.invoke(query)
        return response

    return fn


def test_hotel_reservations_assistant():

    hotels = (
        [
            Hotel(234, "Park Grand London Kensington", "London"),
        ],
    )
    make_reservation_mock = create_mock(make_reservation)
    find_hotels_mock = create_mock(find_hotels, return_value=hotels)
    dependencies = HotelReservationsAssistantDependencies(
        make_reservation=make_reservation_mock,
        find_hotels=find_hotels_mock,
    )
    assistant = HotelReservationsAssistant(dependencies=dependencies)

    user = LLMUser.from_persona(
        """
        My name is John Smith and I'm a helpful user.
        I want to bool a room in Grand London Kensington, from 12th April 2024 to 20th April 2024 for 3 guests.
        """
    )

    conversation = UserConversation(
        assistant=chat_fn(assistant),
        user=user,
        stop_condition=stop_condition(dependencies),
    )

    conversation.start_conversation("I want to book a hotel")
    make_reservation_mock.assert_called_once_with(
        hotel_id=234,
        guest_name="John Smith",
        checkin_date=datetime.date(2024, 4, 12),
        checkout_date=datetime.date(2024, 4, 20),
        guests=3,
    )
