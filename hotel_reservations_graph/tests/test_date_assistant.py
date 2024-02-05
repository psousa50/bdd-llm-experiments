import json

from hamcrest import assert_that, equal_to

from hotel_reservations.date_assistant import create_date_assistant


def get_date(result):
    j = json.loads(result["output"])
    return j["date"]


def test_tomorrow():
    assistant = create_date_assistant()
    result = assistant.invoke({"input": "Today is 2024-04-01. What day is tomorrow?"})
    date = get_date(result)
    assert_that(date, equal_to("2024-04-02"))


def test_next_thursday():
    assistant = create_date_assistant()
    result = assistant.invoke(
        {"input": "Today is 2024-01-23. What day is next thurday?"}
    )
    date = get_date(result)
    assert_that(date, equal_to("2024-01-25"))


def test_next_weekend():
    assistant = create_date_assistant()
    result = assistant.invoke(
        {"input": "Today is 2024-02-05. What day is next weekend?"}
    )
    date = get_date(result)
    assert_that(date, equal_to("2024-02-09"))


def test_next_week():
    assistant = create_date_assistant()
    result = assistant.invoke(
        {"input": "Today is 2024-01-24. What day is the start of next week?"}
    )
    date = get_date(result)
    assert_that(date, equal_to("2024-01-29"))
