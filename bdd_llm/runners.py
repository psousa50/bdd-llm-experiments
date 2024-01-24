from colorama import Fore
from dataclasses import dataclass
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
    ):
        self.assistant = assistant
        self.user = user
        self.stop_condition = stop_condition
        self.max_iterations = max_iterations

        self.chat_log = []

    def start_conversation(self, query: str):
        logger.info("Starting conversation")
        user_response = query
        iterations = 0
        done = False
        while not done:
            llm_response = self.assistant(user_response)
            user_response = self.user.get_input(llm_response)
            logger.info(f"LLM Response: {llm_response}")
            logger.info(f"User Response: {user_response}")
            self.chat_log.append(
                f"{Fore.GREEN}LLM:{Fore.RESET}\n{llm_response['output']}"
            )
            self.chat_log.append(f"{Fore.CYAN}User:{Fore.RESET}\n{user_response}")
            iterations += 1
            done = iterations >= self.max_iterations or self.stop_condition()
