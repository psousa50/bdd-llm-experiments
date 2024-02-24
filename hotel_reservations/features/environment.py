import logging

from dotenv import load_dotenv

from hotel_reservations.chat_open_router import ChatOpenRouter

load_dotenv()


def filter(record):
    print("record.name:", record.name)
    return record.name in ["bdd_llm.mocks", "bdd_llm.runners"]


def before_all(context):
    for handler in logging.root.handlers:
        handler.addFilter(filter)
    llm = ChatOpenRouter(
        model="cognitivecomputations/dolphin-mixtral-8x7b",
        temperature=0.0,
    )
    context.llm = llm
