from colorama import Fore


class ChatMessage:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

    def __repr__(self):
        return f"{self.role}: {self.content}"


class AssistantMessage(ChatMessage):
    def __init__(self, message: str):
        super().__init__("Assistant", message)

    def __str__(self):
        return f"{Fore.GREEN}{self.role}: {self.content}{Fore.RESET}"


class UserMessage(ChatMessage):
    def __init__(self, message: str):
        super().__init__("User", message)

    def __str__(self):
        return f"{Fore.CYAN}{self.role}: {self.content}{Fore.RESET}"
