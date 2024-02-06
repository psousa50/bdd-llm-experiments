# type: ignore

import json

from behave import given, then, when
from hamcrest import assert_that, equal_to

from hotel_reservations.date_assistant import create_date_assistant


def get_date(result):
    j = json.loads(result["output"])
    return j["date"]


@given("I say")
def step_impl(context):  # noqa F811
    context.query = context.text


@when("I ask the assistant to find a date")
def step_impl(context):  # noqa F811
    assistant = create_date_assistant()
    response = assistant.invoke({"input": context.query})
    context.date = get_date(response)


@then("I should see {date}")
def step_impl(context, date):  # noqa F811
    assert_that(context.date, equal_to(date))
