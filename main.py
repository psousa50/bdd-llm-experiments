from bdd_llm.llm_user import DUMB_USER, NORMAL_USER_PROMPT, LLMUser
from bdd_llm.log import Log
from bdd_llm.user import ConsoleUser, DeterministicUser
from hotel_reservations.assistant import HotelReservationsAssistant
from hotel_reservations.core import make_reservation


class LogCollector:
    def __init__(self):
        self.logs = []

    def __call__(self, message):
        self.logs.append(message)
        print(message)


def stop_condition(response: dict) -> bool:
    return response["input"].lower() == "bye"


def start():
    user = ConsoleUser()
    query = "I want to book a room in London"
    user = DeterministicUser(
        [
            query,
            "2",
            "bye",
        ]
    )
    metadata = {
        "name": "Pedro Sousa",
    }
    user = LLMUser(NORMAL_USER_PROMPT, query, metadata)
    assistant = HotelReservationsAssistant(
        user_proxy=user,
        make_reservation=make_reservation,
        stop_condition=stop_condition,
    )
    assistant.start()


if __name__ == "__main__":
    lc = LogCollector()
    Log.set_log_fn(lc)
    Log.set_verbose(True)
    start()

    print("------------------------    LOGS    ------------------------")
    for l in lc.logs:
        print(l)
