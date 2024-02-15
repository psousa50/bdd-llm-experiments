# type: ignore

from datetime import datetime

from behave import given, then, when
from hamcrest import assert_that, greater_than
from langchain_core.messages import AIMessage
from tests.helpers import create_test_conversation

from bdd_llm.conversation_analyzer import ConversationAnalyzer
from bdd_llm.llm_user import LLMUser
from hotel_reservations.core import Hotel

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
    user = LLMUser.from_persona(context.persona)
    current_date_return_value = context.current_date
    conversation, dependencies = create_test_conversation(
        user,
        find_hotels_return_value=context.hotels,
        current_date_return_value=current_date_return_value,
        options={"verbose": verbose},
    )
    context.conversation = conversation
    context.dependencies = dependencies


@when('I say "{query}"')
def step_impl(context, query):  # noqa F811
    context.conversation.start_conversation(query)


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


@then(
    "The conversation should fullfill the following criteria, with a score above {score}"
)
def step_impl(context, score):  # noqa F811
    criteria = context.text.split("\n")
    criteria = [c.strip() for c in criteria if c.strip()]
    conversationAnalyzer = ConversationAnalyzer()
    current_date = AIMessage(content=f"Today is {context.current_date}")
    chat_history = [current_date] + context.conversation.state.chat_history
    response = conversationAnalyzer.invoke(chat_history=chat_history, criteria=criteria)
    assert_that(
        int(response["score"]),
        greater_than(int(score)),
        reason=response["feedback"],
    )
