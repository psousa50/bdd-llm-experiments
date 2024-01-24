from dataclasses import dataclass
from typing import Callable

from bdd_llm.user import UserProxy

Assistant = Callable[[str], str]


class UserConversation:
    def __init__(
        self,
        assistant: Assistant,
        user: UserProxy,
        stop_condition: Callable[[], bool],
        max_iterations: int = 10,
    ):
        self.assistant = assistant
        self.user = user
        self.stop_condition = stop_condition
        self.max_iterations = max_iterations

    def start_conversation(self, query: str):
        q = query
        iterations = 0
        done = False
        while not done:
            response = self.assistant(q)
            q = self.user.get_input(response)
            iterations += 1
            done = iterations >= self.max_iterations or self.stop_condition()
