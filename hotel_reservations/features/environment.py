import logging

from dotenv import load_dotenv

load_dotenv()


def filter(record):
    print("record.name:", record.name)
    return record.name in ["bdd_llm.mocks", "bdd_llm.runners"]


def before_all(context):
    for handler in logging.root.handlers:
        handler.addFilter(filter)
