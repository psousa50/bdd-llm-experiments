from datetime import datetime

from dotenv import load_dotenv

from bdd_llm.conversation_analyzer import ConversationAnalyzer
from bdd_llm.llm_user import LLMUser
from bdd_llm.mocks import create_mock
from bdd_llm.runners import UserConversation
from hotel_reservations.assistant import HotelReservationsAssistant
from hotel_reservations.core import make_reservation
from hotel_reservations.dependencies import HotelReservationsAssistantDependencies

load_dotenv()

verbose = False


def chat_fn(assistant: HotelReservationsAssistant):
    def fn(query: str) -> str:
        response = assistant.invoke(query)
        return response["output"]

    return fn


def start():
    user = LLMUser.from_persona(
        persona="""
        My name is Pedro Sousa and I'm a helpful user.
        I want to book a room in London, starting in May 2 and ending in May 7
        It will be for 4 guests.
        I prefer UK 2
        """,  # noqa E501
    )

    wrapped_make_reservation = create_mock(make_reservation)

    dependencies = HotelReservationsAssistantDependencies(
        make_reservation=wrapped_make_reservation,
        current_date=lambda: datetime(2024, 1, 23),
    )
    assistant = HotelReservationsAssistant(dependencies, verbose=verbose)

    query = "Hi"
    conversation = UserConversation(
        user=user,
        assistant=chat_fn(assistant),
        stop_condition=lambda state: dependencies.make_reservation.called or bye(state),
        options={"verbose": verbose},
    )
    conversation.start_conversation(query)

    print(user.persona)
    print()
    print(query)
    for log in conversation.state.chat_history:
        print(log)

    conversationAnalyzer = ConversationAnalyzer()
    response = conversationAnalyzer.invoke(
        conversation.state.chat_history,
        criteria=[
            "The assistant should greet the user",
            "The assistant should ask for the user name if needed",
            "The assistant should ask for the location of the hotel",
            "The assistant should ask for the check-in date",
            "The assistant should ask for the check-out date",
            "The assistant should ask for the number of guests",
            "The assistant should book a room for Pedro Sousa, hotel with id 2, checkin May 2, checkout May 7, for 4 guests",
        ],
    )
    print(response)


def bye(state):
    return "bye" in state.chat_history[-1].content.lower()


if __name__ == "__main__":
    start()
