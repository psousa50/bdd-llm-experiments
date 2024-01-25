from colorama import Fore
from typing import Callable
import logging
from bdd_llm.user import UserProxy

Assistant = Callable[[str], str]

logger = logging.getLogger(__name__)


class UserConversation:
    def __init__(
        self,
        assistant: Assistant,
        user: UserProxy,
        stop_condition: Callable[[], bool] = lambda: False,
        max_iterations: int = 200,
        options={},
    ):
        self.assistant = assistant
        self.user = user
        self.stop_condition = stop_condition
        self.max_iterations = max_iterations
        self.options = options

        self.chat_log = []

    def start_conversation(self, query: str):
        log_input = f"{Fore.YELLOW}{query}{Fore.RESET}"
        self.log_message(log_input)
        user_response = query
        iterations = 0
        done = False
        while not done:
            llm_response = self.assistant(user_response)
            user_response = self.user.get_input(llm_response)
            log_llm_response = f"{Fore.GREEN}{llm_response['output']}{Fore.RESET}"
            log_user_response = f"{Fore.CYAN}{user_response}{Fore.RESET}"
            self.log_message(log_llm_response)
            self.log_message(log_user_response)
            iterations += 1
            done = iterations >= self.max_iterations or self.stop_condition()

    def log_message(self, message: str):
        if self.options.get("verbose", False):
            print(message)
        self.chat_log.append(message)
