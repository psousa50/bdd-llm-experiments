import json
import logging
import random
from dataclasses import dataclass
from datetime import date
from typing import Callable

logger = logging.getLogger(__name__)


@dataclass
class Hotel:
    id: int
    name: str
    location: str

    def __str__(self):
        return json.dumps(self.__dict__, indent=4)

    def __repr__(self):
        return str(self)


MakeReservation = Callable[[str, str, date, date, int], bool]
CalcReservationPrice = Callable[[str, date, date, int], int]
FindHotels = Callable[[str, str], list[Hotel]]


hotels = [
    Hotel(1, "Hotel UK 1", "London"),
    Hotel(2, "Hotel UK 2", "London"),
    Hotel(3, "Hotel UK 3", "London"),
    Hotel(4, "Hotel France 1", "Paris"),
    Hotel(5, "Hotel France 2", "Paris"),
]


def make_reservation(
    hotel_id: str,
    guest_name: str,
    checkin_date: date,
    checkout_date: date,
    guests: int,
):
    logger.info(
        f"Making reservation for {guest_name} in {hotel_id} from {checkin_date} to {checkout_date} for {guests} guests"
    )
    return True


def calc_reservation_price(
    hotel_id: str, checkin_date: date, checkout_date: date, guests: int
):
    logger.info(
        f"Calculating reservation price for {hotel_id} from {checkin_date} to {checkout_date} for {guests} guests"
    )
    return random.randint(100, 1000)


def find_hotels(name: str = "", location: str = "") -> list[Hotel]:
    logger.info(f"Finding hotels with name {name} and location {location}")
    return [
        hotel for hotel in hotels if name in hotel.name and location in hotel.location
    ]
