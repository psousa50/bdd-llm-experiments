import logging
from datetime import date
import random
from typing import Callable

logger = logging.getLogger(__name__)

MakeReservation = Callable[[str, str, date, date, int], bool]
CalcReservationPrice = Callable[[str, date, date, int], int]
FindHotels = Callable[[str], list[str]]


def make_reservation(
    hotel: str, guest_name: str, checkin_date: date, checkout_date: date, guests: int
):
    logger.info(
        f"Making reservation for {guest_name} in {hotel} from {checkin_date} to {checkout_date} for {guests} guests"
    )
    return True


def calc_reservation_price(
    hotel: str, checkin_date: date, checkout_date: date, guests: int
):
    logger.info(
        f"Calculating reservation price for {hotel} from {checkin_date} to {checkout_date} for {guests} guests"
    )
    return random.randint(100, 1000)


def find_hotels(location: str) -> list[str]:
    hotels = {
        "London": ["Hotel UK 1", "Hotel UK 2", "Hotel UK 3"],
        "Paris": ["Hotel France 1", "Hotel France 2", "Hotel France 3"],
    }
    return hotels[location] if location in hotels else []
