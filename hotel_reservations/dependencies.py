from datetime import date
from typing import Callable
from hotel_reservations.core import (
    FindHotels,
    MakeReservation,
    find_hotels,
    make_reservation,
)


def current_date():
    return date.today()


class HotelReservationsAssistantDependencies:
    def __init__(
        self,
        find_hotels: FindHotels = find_hotels,
        make_reservation: MakeReservation = make_reservation,
        current_date: Callable[[], date] = current_date,
    ):
        self.find_hotels = find_hotels
        self.make_reservation = make_reservation
        self.current_date = current_date
