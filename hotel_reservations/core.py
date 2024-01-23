from datetime import date
from typing import Callable

from bdd_llm.log import Log

MakeReservation = Callable[[str, str, date, date, int], bool]

log = Log("make_reservation function")


def make_reservation(
    hotel: str, guest_name: str, start_date: date, end_date: date, guests: int
):
    log(
        f"Making reservation for {guest_name} in {hotel} from {start_date} to {end_date} for {guests} guests"
    )
    return True
