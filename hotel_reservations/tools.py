from typing import Optional, Type
from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)
from datetime import date
from langchain_core.tools import tool
from langchain.pydantic_v1 import BaseModel, Field

from langchain_core.tools import BaseTool

from hotel_reservations.core import MakeReservation


@tool
def find_hotels_tool(location: str) -> list[str]:
    """Useful to find hotels near a location."""
    hotels = {
        "London": ["Hotel UK 1", "Hotel UK 2", "Hotel UK 3"],
        "Paris": ["Hotel France 1", "Hotel France 2", "Hotel France 3"],
    }
    return hotels[location]


# @tool("make_reservation")
# def make_reservation_tool(
#     hotel: str, guest_name: str, checkin: date, checkout: date, guests: int
# ) -> str:
#     """Useful for making a reservation."""
#     make_reservation(hotel, guest_name, checkin, checkout, guests)
#     return f"Reservation made with {hotel} for {guest_name} from {checkin} to {checkout} for {guests} guests."


class MakeReservationInput(BaseModel):
    hotel: str = Field(description="The hotel name.")
    guest_name: str = Field(description="The guest name.")
    checkin: date = Field(description="The checkin date in the format YYYY-MM-DD.")
    checkout: date = Field(description="The checkout date in the format YYYY-MM-DD.")
    guests: int = Field(description="The number of guests.")


class MakeReservationTool(BaseTool):
    name = "make_reservation"
    description = "Useful for making a reservation."
    args_schema: Type[BaseModel] = MakeReservationInput

    def _run(
        self,
        hotel: str,
        guest_name: str,
        checkin: date,
        checkout: date,
        guests: int,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Useful for making a reservation."""
        make_reservation = self.metadata["make_reservation"]
        make_reservation(hotel, guest_name, checkin, checkout, guests)
        return f"Reservation made with {hotel} for {guest_name} from {checkin} to {checkout} for {guests} guests."


@tool
def current_date_tool() -> date:
    """Useful for getting the current date."""
    return date.today()


def build_tools(make_reservation: MakeReservation):
    tools = [
        MakeReservationTool(metadata={"make_reservation": make_reservation}),
        find_hotels_tool,
        current_date_tool,
    ]
    return tools
