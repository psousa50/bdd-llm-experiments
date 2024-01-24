import logging
from unittest.mock import create_autospec

logger = logging.getLogger(__name__)


def create_mock(original_func, return_value=None):
    mock_func = create_autospec(
        original_func,
        return_value=return_value,
        side_effect=lambda *args, **kwargs: logger.info(
            f"Calling {original_func.__name__} with args={args} and kwargs={kwargs}"
        ),
    )
    mock_func.__annotations__ = original_func.__annotations__
    mock_func.__name__ = original_func.__name__
    return mock_func


def wrap(original_func, mock_func):
    mock_func.__annotations__ = original_func.__annotations__
    mock_func.__name__ = original_func.__name__
    return mock_func
