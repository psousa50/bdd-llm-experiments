# type: ignore

from datetime import datetime

from behave import given, then, when
from hamcrest import assert_that, greater_than
from langchain_core.messages import AIMessage, HumanMessage
from tests.conversation_analyzer import ConversationAnalyzer
from tests.llm_user import llm_user, llm_user_node
from tests.mocks import create_mock

from hotel_reservations.assistant import (
    DependenciesOptions,
    HotelReservationsAssistantDependencies,
    hotel_reservations_assistant,
)
from hotel_reservations.core import Hotel, find_hotels, make_reservation

verbose = False


def format_date(date):
    return datetime.strptime(date, "%Y-%m-%d").date()


@given("I'm a user with the following persona")
def step_impl(context):
    context.persona = context.text
    context.current_date = datetime.now().date()
    context.hotels = []


@given("Today is {today}")
def step_impl(context, today):  # noqa F811
    context.current_date = format_date(today)


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

    model = "gpt-3.5-turbo-0125"
    dependencies = HotelReservationsAssistantDependencies(
        find_hotels=create_mock(find_hotels, return_value=context.hotels),
        make_reservation=create_mock(make_reservation),
        current_date=lambda: context.current_date,
        options=DependenciesOptions(model=model),
    )
    user = llm_user_node(llm_user(context.persona))
    context.assistant = hotel_reservations_assistant(
        user=user,
        dependencies=dependencies,
    )
    context.dependencies = dependencies


@when('I say "{query}"')
def step_impl(context, query):  # noqa F811
    context.messages = context.assistant.invoke([HumanMessage(content=query)])


@then("The assistant should fetch the current date")
def step_impl(context):  # noqa F811
    context.dependencies.current_date.assert_called_once()


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


@then("The conversation should make sense, with a score above {score}")
def step_impl(context, score):  # noqa F811
    conversationAnalyzer = ConversationAnalyzer()
    current_date = AIMessage(content=f"Today is {context.current_date}")
    chat_history = [current_date] + context.messages
    response = conversationAnalyzer.invoke(chat_history)
    assert_that(
        int(response["score"]),
        greater_than(int(score)),
        reason=response["feedback"],
    )
