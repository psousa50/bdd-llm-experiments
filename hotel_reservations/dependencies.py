from datetime import date
from typing import Callable
from hotel_reservations.core import (
    FindHotels,
    MakeReservation,
    CalcReservationPrice,
    find_hotels,
    make_reservation,
    calc_reservation_price,
)


def current_date():
    return date.today()


def current_year():
    return date.today().year


class HotelReservationsAssistantDependencies:
    def __init__(
        self,
        find_hotels: FindHotels = find_hotels,
        make_reservation: MakeReservation = make_reservation,
        calc_reservation_price: CalcReservationPrice = calc_reservation_price,
        current_date: Callable[[], date] = current_date,
        current_year: Callable[[], date] = current_year,
    ):
        self.find_hotels = find_hotels
        self.make_reservation = make_reservation
        self.calc_reservation_price = calc_reservation_price
        self.current_date = current_date
        self.current_year = current_year
