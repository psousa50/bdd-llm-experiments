import json
from bdd_llm.conversation_analyzer import ConversationAnalyzer
from bdd_llm.messages import AssistantMessage, UserMessage


chat_history = [
    UserMessage("I want to book a room"),
    AssistantMessage(
        """
        Sure, I can help you with that. I need some information from you. Could you please provide me with the following details?

        1. Your name.
        2. The name or location of the hotel.
        3. The check-in and check-out dates.
        4. The number of guests.
    """  # noqa E501
    ),
    UserMessage(
        """
        1. My name is Pedro Sousa.
        2. I prefer the hotel UK 2 in London.
        3. I want to check-in on the 3rd of February and check-out after 3 days.
        4. There will be two guests.
    """
    ),
    AssistantMessage(
        """
        Here are the details of your reservation:

        - Guest Name: Pedro Sousa
        - Hotel: Hotel UK 2, London
        - Check-in Date: 3rd February 2024
        - Check-out Date: 6th February 2024
        - Number of Guests: 2
        - Total Price: $809

        Please confirm if all the details are correct so that I can proceed with the reservation.
    """
    ),
    UserMessage(
        "I'm sorry, but as a user, I can't confirm the reservation. You should respond to the assistant's question."
    ),
    AssistantMessage(
        """
        Great! Your reservation at Hotel UK 2, London from 3rd February 2024 to 6th February 2024 for 2 guests has been successfully made. Enjoy your stay!
        """  # noqa E501
    ),
    UserMessage("bye"),
]

conversationAnalyzer = ConversationAnalyzer()
response = conversationAnalyzer.invoke(chat_history)
response_json = json.loads(response.content)
print(response_json)
