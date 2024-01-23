from abc import ABC, abstractmethod


def stop_condition(response: dict) -> bool:
    return response["input"].lower() == "bye"


class UserProxy:
    @abstractmethod
    def get_input(self, question: str):
        pass


class ConsoleUser(UserProxy):
    def __init__(self, query="", metadata={}):
        self.query = query
        self.metadata = metadata

    def get_input(self, question):
        print(question)
        return input("You: ")


class DeterministicUser(UserProxy):
    def __init__(self, responses: list[str], query="", metadata={}):
        self.responses = responses
        self.query = query
        self.metadata = metadata
        self.response_index = 0

    def get_input(self, question):
        response = self.responses[self.response_index]
        self.response_index += 1
        return response
