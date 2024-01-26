from dataclasses import dataclass
from colorama import Fore
from typing import Callable
import logging
from bdd_llm.messages import AssistantMessage, UserMessage, ChatMessage
from bdd_llm.user import UserProxy

Assistant = Callable[[str], str]

logger = logging.getLogger(__name__)


@dataclass
class UserConversationState:
    chat_history: list[ChatMessage]


class UserConversation:
    def __init__(
        self,
        assistant: Assistant,
        user: UserProxy,
        stop_condition: Callable[[UserConversationState], bool] = lambda: False,
        max_iterations: int = 10,
        options={},
    ):
        self.assistant = assistant
        self.user = user
        self.stop_condition = stop_condition
        self.max_iterations = max_iterations
        self.options = options

        self.chat_history = []

    def start_conversation(self, query: str):
        self.chat_history.append(UserMessage(query))
        log_input = f"{Fore.YELLOW}{query}{Fore.RESET}"
        self.log_message(log_input)
        user_response = query
        iterations = 0
        done = False
        while not done:
            llm_response = self.assistant(user_response)
            llm_response = llm_response["output"]
            user_response = self.user.get_input(llm_response, self.chat_history)

            self.log_message(AssistantMessage(llm_response))
            self.log_message(UserMessage(user_response))

            iterations += 1
            state = UserConversationState(self.chat_history)
            done = iterations >= self.max_iterations or self.stop_condition(state)

    def log_message(self, message: ChatMessage):
        if self.options.get("verbose", False):
            print(message)
        self.chat_history.append(message)

    def user_message(self, message: str):
        return f"User:{message}"

    def llm_message(self, message: str):
        return f"Assistant:{message}"
