from unittest.mock import Mock

from langchain_core.tools import StructuredTool

from hotel_reservations.core import find_hotels

find_hotels_mock = Mock()
find_hotels_mock.__annotations__ = find_hotels.__annotations__
find_hotels_mock.__name__ = find_hotels.__name__
find_hotels_mock.return_value = ["H1", "H2"]

tool = (
    StructuredTool.from_function(
        func=find_hotels_mock,
        name="find_hotels",
        description="Useful to find hotels near a location.",
    ),
)
