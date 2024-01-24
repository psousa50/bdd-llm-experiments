from unittest.mock import create_autospec


def create_mock(original_func, return_value=None):
    mock_func = create_autospec(original_func, return_value=return_value)
    mock_func.__annotations__ = original_func.__annotations__
    mock_func.__name__ = original_func.__name__
    return mock_func
