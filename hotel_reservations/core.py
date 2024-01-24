import logging
from datetime import date
from typing import Callable

logger = logging.getLogger(__name__)

MakeReservation = Callable[[str, str, date, date, int], bool]
FindHotels = Callable[[str], list[str]]


def make_reservation(
    hotel: str, guest_name: str, start_date: date, end_date: date, guests: int
):
    logger.info(
        f"Making reservation for {guest_name} in {hotel} from {start_date} to {end_date} for {guests} guests"
    )
    return True


def find_hotels(location: str) -> list[str]:
    hotels = {
        "London": ["Hotel UK 1", "Hotel UK 2", "Hotel UK 3"],
        "Paris": ["Hotel France 1", "Hotel France 2", "Hotel France 3"],
    }
    return hotels[location]
