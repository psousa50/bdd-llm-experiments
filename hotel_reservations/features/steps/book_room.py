from bdd_llm.llm_user import LLMUser
from behave import given, when, then
from datetime import datetime

from hotel_reservations.core import Hotel
from tests.hotel_reservations_assistant_test import create_test_conversation

test_config = {}


def before_scenario(context):
    context.current_date = datetime.now().date()
    context.current_year = datetime.now().year
    print("Before scenario executed")


def format_date(date):
    return datetime.strptime(date, "%Y-%m-%d").date()


@given("I'm a user with the following persona")
def step_impl(context):
    context.persona = context.text
    context.current_date = datetime.now().date()
    context.current_year = datetime.now().year


@given("Today is {today}")
def step_impl(context, today):  # noqa F811
    context.current_date = format_date(today)


@given("The year is {year}")
def step_impl(context, year):  # noqa F811
    context.current_year = int(year)


@given("We have the following hotels in {location}")
def step_impl(context, location):  # noqa F811
    hotels = []
    for row in context.table:
        hotels.append(Hotel(row["Id"], row["Name"], location))
    context.hotels = hotels


@given("We have the following hotels available")
def step_impl(context):  # noqa F811
    hotels = []
    for row in context.table:
        hotels.append(Hotel(row["Id"], row["Name"], row["Location"]))
    context.hotels = hotels


@when("I start a conversation with an Assistant")
def step_impl(context):  # noqa F811
    user = LLMUser.from_persona(context.persona)
    current_date_return_value = context.current_date
    current_year_return_value = context.current_year
    conversation, dependencies = create_test_conversation(
        user,
        find_hotels_return_value=context.hotels,
        current_date_return_value=current_date_return_value,
        current_year_return_value=current_year_return_value,
    )
    context.conversation = conversation
    context.dependencies = dependencies


@when('I say "{query}"')
def step_impl(context, query):  # noqa F811
    context.conversation.start_conversation(query)


@then("The assistant should fetch the current date")
def step_impl(context):  # noqa F811
    context.dependencies.current_date.assert_called_once()


@then("The assistant should fetch the current year")
def step_impl(context):  # noqa F811
    context.dependencies.current_year.assert_called_once()


@then(
    "The assistant should book a room for {name}, in the hotel with id {hotel_id}, starting in {checkin_date} and ending in {checkout_date}, for {guests} people"  # noqa E501
)
def step_impl(  # noqa F811
    context, name, hotel_id, checkin_date, checkout_date, guests
):
    context.dependencies.make_reservation.assert_called_once_with(
        int(hotel_id),
        name,
        format_date(checkin_date),
        format_date(checkout_date),
        int(guests),
    )
