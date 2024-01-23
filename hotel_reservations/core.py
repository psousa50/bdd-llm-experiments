from datetime import date
from typing import Callable

MakeReservation = Callable[[str, str, date, date, int], bool]


def make_reservation(
    hotel: str, guest_name: str, start_date: date, end_date: date, guests: int
):
    print(
        f"Making reservation for {guest_name} in {hotel} from {start_date} to {end_date} for {guests} guests"
    )
    return True
