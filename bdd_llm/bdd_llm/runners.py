import logging
from typing import Any, Callable

from bdd_llm.messages import AssistantMessage, ChatMessage, UserMessage
from bdd_llm.user import UserProxy

Assistant = Callable[[str], str]

logger = logging.getLogger(__name__)


class UserConversationState:
    def __init__(self, chat_history: list[ChatMessage] = []):
        self.chat_history = chat_history

    def add_message(self, message: ChatMessage):
        self.chat_history.append(message)


class UserConversation:
    def __init__(
        self,
        assistant: Assistant,
        user: UserProxy,
        stop_condition: Callable[[UserConversationState], bool] = lambda _: False,
        max_iterations: int = 10,
        options={},
    ):
        self.assistant = assistant
        self.user = user
        self.stop_condition = stop_condition
        self.max_iterations = max_iterations
        self.options = options

        self.state = UserConversationState()

    def start_conversation(self, query: str):
        self.state.add_message(UserMessage(query))
        user_response = query
        iterations = 0
        done = False
        while not done:
            llm_response = self.assistant(user_response)
            user_response = self.user.get_input(llm_response, self.state.chat_history)

            self.log_message(AssistantMessage(llm_response))
            self.log_message(UserMessage(user_response))

            iterations += 1
            done = iterations >= self.max_iterations or self.stop_condition(self.state)

        for message in self.state.chat_history:
            logger.info(message)

        return self.state

    def log_message(self, message: ChatMessage):
        if self.options.get("verbose", False):
            print(message)
        self.state.add_message(message)

    def user_message(self, message: str):
        return f"User:{message}"

    def llm_message(self, message: str):
        return f"Assistant:{message}"
