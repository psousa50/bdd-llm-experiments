from bdd_llm.user_agent import build_agent


def stop_condition(response: dict) -> bool:
    return response["input"].lower() == "bye"


class UserProxy:
    pass


class RegularUser(UserProxy):
    def __init__(self, query, metadata):
        self.query = query

        self.agent = build_agent(query, metadata)

    def get_input(self, output):
        print("LLM: " + output)
        response = self.agent.invoke({"input": output})
        print("User response: " + response)
        return response


class ConsoleUser(UserProxy):
    def __init__(self, query="", metadata={}):
        self.query = query
        self.metadata = metadata

    def get_input(self, output):
        print(output)
        return input("You: ")


class DeterministicUser(UserProxy):
    def __init__(self, responses: list[str], query="", metadata={}):
        self.responses = responses
        self.query = query
        self.metadata = metadata
        self.response_index = 0

    def get_input(self, output):
        response = self.responses[self.response_index]
        self.response_index += 1
        return response
