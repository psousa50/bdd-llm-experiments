from colorama import Fore


class ChatMessage:
    def __init__(self, role: str, message: str):
        self.role = role
        self.message = message

    def __repr__(self):
        return f"{self.role}: {self.message}"


class AssistantMessage(ChatMessage):
    def __init__(self, message: str):
        super().__init__("Assistant", message)

    def __str__(self):
        return f"{Fore.GREEN}{self.role}: {self.message}{Fore.RESET}"


class UserMessage(ChatMessage):
    def __init__(self, message: str):
        super().__init__("User", message)

    def __str__(self):
        return f"{Fore.CYAN}{self.role}: {self.message}{Fore.RESET}"
