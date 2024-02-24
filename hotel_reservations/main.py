from datetime import datetime

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_experimental.llms.ollama_functions import OllamaFunctions
from langchain_openai import ChatOpenAI  # noqa E402

from bdd_llm.conversation_analyzer import ConversationAnalyzer
from bdd_llm.llm_user import LLMUser
from bdd_llm.mocks import create_mock
from bdd_llm.runners import UserConversation
from hotel_reservations.assistant import HotelReservationsAssistant
from hotel_reservations.chat_open_router import ChatOpenRouter
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
    llm = ChatOpenRouter(
        model="mistralai/mixtral-8x7b-instruct",
        temperature=0.0,
    )
    llm = ChatOpenAI(
        model="gpt-4-turbo-preview",
        temperature=0.0,
    )
    # llm = OllamaFunctions(
    #     model="llama2",
    #     temperature=0,
    # )  # type: ignore

    user = LLMUser.from_persona(
        persona="""
        My name is Pedro Sousa and I'm a helpful user.
        I want to book a room in London, starting in May 2 and ending in May 7
        It will be for 4 guests.
        I prefer UK 2
        """,  # noqa E501
        llm=llm,
    )

    wrapped_make_reservation = create_mock(make_reservation)

    dependencies = HotelReservationsAssistantDependencies(
        make_reservation=wrapped_make_reservation,
        current_date=lambda: datetime(2024, 1, 23),
    )
    assistant = HotelReservationsAssistant(llm, dependencies, verbose=verbose)

    query = "Hi"
    conversation = UserConversation(
        user=user,
        assistant=chat_fn(assistant),
        stop_condition=lambda state: dependencies.make_reservation.called or bye(state),
        options={"verbose": verbose},
    )
    conversation.start_conversation(query)

    print(f"Persona:\n{user.persona}")
    print()
    print(f"Query:\n{query}")
    for msg in conversation.state.chat_history:
        print(msg.pretty_print())

    conversationAnalyzer = ConversationAnalyzer()
    response = conversationAnalyzer.invoke(
        conversation.state.chat_history,
        criteria=[
            "greet the user",
            "ask for the user name if needed",
            "ask for the location of the hotel",
            "ask for the check-in date",
            "ask for the check-out date",
            "ask for the number of guests",
            "book a room for Pedro Sousa, hotel with id 2, checkin May 2, checkout May 7, for 4 guests",
        ],
    )
    print("Analyzed conversation")
    print(response)


def bye(state):
    return "bye" in state.chat_history[-1].content.lower()


if __name__ == "__main__":
    start()
