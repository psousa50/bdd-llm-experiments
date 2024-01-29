import logging
from unittest.mock import create_autospec

logger = logging.getLogger(__name__)


def create_mock(original_func, return_value=None):
    mock_func = create_autospec(
        original_func,
        side_effect=log_call(original_func, return_value),
    )
    mock_func.__annotations__ = original_func.__annotations__
    mock_func.__name__ = original_func.__name__
    return mock_func


def wrap(original_func, return_value=None):
    mock_func = create_autospec(
        original_func,
        side_effect=log_call(original_func, return_value),
    )
    mock_func.__annotations__ = original_func.__annotations__
    mock_func.__name__ = original_func.__name__
    return mock_func


def log_call(func, return_value):
    def wrapper(*args, **kwargs):
        logger.info(
            f"TOOL CALLED: {func.__name__} with args: {args} and kwargs: {kwargs}"
        )
        return func(*args, **kwargs) if return_value is None else return_value

    return wrapper
