from bdd_llm.user import ConsoleUser, DeterministicUser, RegularUser
from hotel_reservations.assistant import HotelReservationsAssistant
from hotel_reservations.core import make_reservation
from hotel_reservations.tools import MakeReservationTool


def stop_condition(response: dict) -> bool:
    return response["input"].lower() == "bye"


def start():
    user = ConsoleUser()
    user = DeterministicUser(
        [
            "My name is Pedro Sousa. I want to book a room in London, for 3 days, starting 12 Feb. It's for two guests",
            "2",
            "bye",
        ]
    )
    query = "My name is Pedro Sousa. I want to book a room in London, for 3 days, starting 12 Feb of 2024. It's for two guests"
    metadata = {
        "name": "Pedro Sousa",
    }
    user = RegularUser(query, metadata)
    assistant = HotelReservationsAssistant(
        user_proxy=user,
        make_reservation=make_reservation,
        stop_condition=stop_condition,
    )
    assistant.start()


if __name__ == "__main__":
    start()
