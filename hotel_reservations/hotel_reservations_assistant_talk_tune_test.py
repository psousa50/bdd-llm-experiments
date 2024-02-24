import functools
import time
from datetime import date, timedelta
from random import choice
from typing import Callable

from dotenv import load_dotenv
from hamcrest import assert_that, less_than
from langchain_core.language_models.base import BaseLanguageModel

from bdd_llm.llm_user import LLMUser
from bdd_llm.mocks import create_mock
from hotel_reservations.assistant import HotelReservationsAssistant
from hotel_reservations.core import (
    Hotel,
    calc_reservation_price,
    find_hotels,
    make_reservation,
)
from hotel_reservations.dependencies import (
    HotelReservationsAssistantDependencies,
    current_date,
)
from hotel_reservations.hotel_reservations.chat_open_router import ChatOpenRouter

load_dotenv()


class User:
    def __init__(self, persona: str, metadata: dict = {}, goal=""):
        self.persona = persona
        self.metadata = metadata
        self.goal = goal

    def with_goal(self, goal: str):
        self.goal = goal
        return self


class ChatMessage:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content


class AIMessage(ChatMessage):
    def __init__(self, content: str):
        super().__init__("AI", content)


class HumanMessage(ChatMessage):
    def __init__(self, content: str):
        super().__init__("Human", content)


class TalkState:
    def __init__(self, chat_history=[]):
        self.chat_history = chat_history
        self.iterations = 0
        self.runs = 0
        self.fails = 0
        self.context = {}
        self.success = False

    def add_message(self, message):
        self.chat_history.append(message)

    def fails_percentage(self):
        p = self.fails / self.runs
        return round(p, 3)


class Users:
    def __init__(self, *users: User):
        self.users = users

        self._cycle = False
        self.llm_users = []
        self.counter = 0

    def cycle(self):
        self._cycle = True
        return self

    def build_llm_users(self, goal):
        llm = build_llm()
        self.llm_users = [
            LLMUser.from_parts(
                llm=llm,
                persona=user.persona,
                metadata=user.metadata,
                goal=goal,
            )
            for user in self.users
        ]

    def next(self) -> LLMUser:
        if self._cycle:
            c = self.counter
            self.counter = (self.counter + 1) % len(self.llm_users)
            user = self.llm_users[c]
        else:
            user = choice(self.llm_users)
        return user


StopCondition = Callable[[TalkState], bool]
Scenario = dict
Assistant = Callable[[str], str]
AssistantBuilder = Callable[[Scenario], tuple[Assistant, dict]]
Assertion = Callable[[TalkState], None]


class Talk:
    def __init__(self):
        self.state = TalkState()
        self.scenario = {}
        self.query = ""
        self.stop_condition = self.default_stop_condition
        self.max_iterations = 10
        self.assertions: list[Assertion] = []
        self.global_assertions: list[Assertion] = []

    def default_stop_condition(self, state: TalkState):
        return state.iterations >= self.max_iterations

    def using(self, users: Users):
        self.users = users
        return self

    def given(self, scenario: dict):
        self.scenario = scenario
        return self

    def talking_to(self, assistant_builder: AssistantBuilder):
        self.assistant_builder = assistant_builder
        return self

    def saying(self, query: str):
        self.query = query
        return self

    def should(self, assertion):
        self.assertions.append(assertion)
        return self

    def until(self, stop_condition: StopCondition):
        self.stop_condition = stop_condition
        return self

    def run(self, count):
        self.state.success = False
        self.state.runs = count
        self.state.fails = 0
        goal = self.scenario["goal"]

        for r in range(count):
            print(f"Starting run {r + 1}", end=" ... ", flush=True)
            start_time = time.time()
            self.users.build_llm_users(goal)
            assistant, context = self.assistant_builder(self.scenario)
            self.state.context = context
            success = self._run_conversation(assistant)
            end_time = time.time()
            execution_time = end_time - start_time
            execution_time = round(execution_time, 2)
            if not success:
                self.state.fails += 1
            print(
                f" took {timedelta(seconds= execution_time)} seconds, with {'success' if success else 'failure'}"
            )

        outcomes = [self._check(assertion) for assertion in self.assertions]
        self.state.success = all(outcomes)
        return self

    def _run_conversation(self, assistant: Assistant):
        self.state.add_message(HumanMessage(content=self.query))
        user_response = self.query
        done = False
        self.state.iterations = 0
        while not done:
            user = self.users.next()
            llm_response = assistant(user_response)
            user_response = user.get_input(llm_response)

            self.state.add_message(AIMessage(content=llm_response))
            self.state.add_message(HumanMessage(content=user_response))

            self.state.iterations += 1
            done = self.state.iterations >= self.max_iterations or self.stop_condition(
                self.state
            )

        outcomes = [self._check(assertion) for assertion in self.assertions]
        success = all(outcomes)
        return success

    def _check(self, assertion: Assertion):
        try:
            assertion(self.state)
            return True
        except AssertionError as e:
            print("Assertion failed:", e)
            return False

    def assertion(self, assertion: Assertion):
        self.global_assertions.append(assertion)
        return self


def create_dependencies(
    find_hotels_return_value=["H1", "H2", "H3"],
    calc_reservation_price_return_value=100,
    current_date_return_value=date(2024, 1, 1),
):
    dependencies = HotelReservationsAssistantDependencies(
        find_hotels=create_mock(find_hotels, return_value=find_hotels_return_value),
        calc_reservation_price=create_mock(
            calc_reservation_price, return_value=calc_reservation_price_return_value
        ),
        make_reservation=create_mock(make_reservation, return_value=True),
        current_date=create_mock(current_date, return_value=current_date_return_value),
    )
    return dependencies


def build_assistant(
    llm: BaseLanguageModel,
    scenario: Scenario,
) -> tuple[Assistant, dict]:
    dependencies = HotelReservationsAssistantDependencies(
        find_hotels=create_mock(find_hotels, return_value=scenario["hotels"]),
        make_reservation=create_mock(make_reservation, return_value=True),
        current_date=create_mock(current_date, return_value=scenario["current_date"]),
    )
    dependencies = create_dependencies(
        find_hotels_return_value=scenario["hotels"],
        current_date_return_value=scenario["current_date"],
    )

    assistant = HotelReservationsAssistant(llm=llm, dependencies=dependencies)

    def assistant_fn(query: str) -> str:
        response = assistant.invoke(query)
        return response["output"]

    context = {"dependencies": dependencies}
    return (assistant_fn, context)


def user_said_bye(state: TalkState):
    return state.chat_history[-1].content.lower() == "bye"


def talk_to_book_a_room_with_all_the_information():
    users = Users(
        User(
            persona="I'm a helpful user",
            metadata={"name": "Pedro Sousa"},
        ),
        User(
            persona="I'm a dumb user and I can ony anwser one question at a time",
            metadata={"name": "Pedro Sousa"},
        ),
    )
    scenario = {
        "goal": "My name is Pedro Sousa and I want to book a room in hotel Britannia, starting 12 Feb and ending 15 Feb. It's for two guests.",  # noqa E501
        "current_date": "2024-01-01",
        "hotels": [Hotel(123, "Britannia International Hotel", "London")],
    }

    return (
        Talk()
        .given(scenario)
        .using(users.cycle())
        .talking_to(llm_build_assistant())
        .saying("I want to book a room")
        .should(
            lambda state: state.context[
                "dependencies"
            ].make_reservation.assert_called_once_with(
                123,
                "Pedro Sousa",
                date(2024, 2, 12),
                date(2024, 2, 15),
                2,
            )
        )
        .until(
            lambda state: state.context["dependencies"].make_reservation.called
            or user_said_bye(state)
        )
        .run(10)
        .assertion(lambda state: assert_that(state.fails_percentage(), less_than(0.9)))
    )


def talk_to_book_a_room_with_relative_dates():
    users = Users(
        User(
            persona="I'm a helpful user",
            metadata={"name": "Pedro Sousa"},
        ),
    )
    scenario = {
        "goal": "Book a room in the Britannia International Hotel, for the next weekend, starting Friday, for me, my wife and our two kids",  # noqa E501
        "current_date": "2024-01-23",
        "hotels": [
            Hotel(611, "Britannia International Hotel", "London"),
            Hotel(29, "Park Grand London Kensington", "London"),
            Hotel(52, "Park Plaza Westminster Bridge London", "London"),
        ],
    }

    return (
        Talk()
        .given(scenario)
        .using(users)
        .talking_to(llm_build_assistant())
        .saying("I want to book a room")
        .should(
            lambda state: state.context[
                "dependencies"
            ].make_reservation.assert_called_once_with(
                611,
                "Pedro Sousa",
                date(2024, 1, 26),
                date(2024, 1, 28),
                4,
            )
        )
        .until(
            lambda state: state.context["dependencies"].make_reservation.called
            or user_said_bye(state)
        )
        .run(10)
        .assertion(lambda state: assert_that(state.fails_percentage(), less_than(0.9)))
    )


def talk_to_book_a_room_for_next_thursday():
    users = Users(
        User(
            persona="I'm a helpful user",
            metadata={"name": "Pedro Sousa"},
        ),
    )
    scenario = {
        "goal": "Book a room in the Britannia International Hotel, starting next Thursday, for 3 days, for me, my wife and our two kids",  # noqa E501
        "current_date": "2024-01-23",
        "hotels": [
            Hotel(611, "Britannia International Hotel", "London"),
            Hotel(29, "Park Grand London Kensington", "London"),
            Hotel(52, "Park Plaza Westminster Bridge London", "London"),
        ],
    }

    return (
        Talk()
        .given(scenario)
        .using(users)
        .talking_to(llm_build_assistant())
        .saying("I want to book a room")
        .should(
            lambda state: state.context[
                "dependencies"
            ].make_reservation.assert_called_once_with(
                611,
                "Pedro Sousa",
                date(2024, 1, 25),
                date(2024, 1, 28),
                4,
            )
        )
        .until(
            lambda state: state.context["dependencies"].make_reservation.called
            or user_said_bye(state)
        )
        .run(10)
        .assertion(lambda state: assert_that(state.fails_percentage(), less_than(0.9)))
    )


def start():
    tests = [
        talk_to_book_a_room_with_all_the_information,
        talk_to_book_a_room_with_relative_dates,
        talk_to_book_a_room_for_next_thursday,
    ]
    total_runs = 0
    total_fails = 0
    for test in tests:
        talk = test()
        total_runs += talk.state.runs
        total_fails += talk.state.fails
        print(f"Test failed {talk.state.fails} times out of {talk.state.runs} runs")
        print(f"Success: {talk.state.success}")

    print(f"Total runs: {total_runs}")
    print(f"Total fails: {total_fails}")
    print(f"Failure rate: {total_fails / total_runs}")


def build_llm():
    llm = ChatOpenRouter(
        model="cognitivecomputations/dolphin-mixtral-8x7b",
        temperature=0.0,
    )
    return llm


def llm_build_assistant():
    llm = build_llm()
    return functools.partial(build_assistant, llm)


if __name__ == "__main__":
    start()
