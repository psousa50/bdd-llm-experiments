# flake8: noqa

from openai import OpenAI

client = OpenAI()

message = {
    "messages": [
        {
            "role": "system",
            "content": "\nYou have a list of tools that you can use to help you make a reservation.\nDon't EVER call the same tool twice with the same arguments, the response will ALWAYS be the same.\nYou should ask the user for the information needed to make the reservation, don't guess it.\nThe name of the guest is mandatory to make the reservation.\nIf should try to find out what's the current year, don't assume it.\nif you realize that you cannot make the reservation, you should say it.\nWhen you have all the information needed to make the reservation, show the user the reservation details, including the price and ask for confirmation.\nIf the user confirms, make the reservation.\n",
        },
        {"role": "user", "content": "I want to book a room"},
        {
            "role": "assistant",
            "content": "Sure, I can help you with that. Could you please provide me with the following details?\n\n1. Your name.\n2. The name or location of the hotel you want to book.\n3. The check-in and check-out dates.\n4. The number of guests.",
        },
        {
            "role": "user",
            "content": "1. My name is Pedro Sousa.\n2. I want to book a room at the hotel UK 2 in London.\n3. I want to check-in on the 3rd of February 2024 and check-out after 3 days.\n4. There will be two guests.",
        },
        {
            "role": "assistant",
            "content": "The reservation details are as follows:\n\n- Guest Name: Pedro Sousa\n- Hotel Name: Hotel UK 2\n- Location: London\n- Check-in Date: 3rd of February 2024\n- Check-out Date: 6th of February 2024\n- Number of Guests: 2\n- Total Price: \u00a3100\n\nPlease confirm if the details are correct so that I can proceed with the reservation.",
        },
        {
            "role": "user",
            "content": "Yes, the details are correct. Please proceed with the reservation.",
        },
    ],
    "model": "gpt-4",
    "functions": [
        {
            "name": "current_date",
            "description": "current_date() - Useful to get the current date.",
            "parameters": {
                "title": "current_dateSchemaSchema",
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "current_year",
            "description": "current_year() - Useful to find the current year.",
            "parameters": {
                "title": "current_yearSchemaSchema",
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "find_hotels",
            "description": "find_hotels(name: str = '', location: str = '') -> list[hotel_reservations.core.Hotel] - Useful to find hotels by name and/or location.",
            "parameters": {
                "title": "find_hotelsSchemaSchema",
                "type": "object",
                "properties": {
                    "name": {"title": "Name", "default": "", "type": "string"},
                    "location": {"title": "Location", "default": "", "type": "string"},
                },
            },
        },
        {
            "name": "make_reservation",
            "description": "make_reservation(hotel_id: int, guest_name: str, checkin_date: datetime.date, checkout_date: datetime.date, guests: int) - Useful to make a reservation.",
            "parameters": {
                "title": "make_reservationSchemaSchema",
                "type": "object",
                "properties": {
                    "hotel_id": {"title": "Hotel Id", "type": "integer"},
                    "guest_name": {"title": "Guest Name", "type": "string"},
                    "checkin_date": {
                        "title": "Checkin Date",
                        "type": "string",
                        "format": "date",
                    },
                    "checkout_date": {
                        "title": "Checkout Date",
                        "type": "string",
                        "format": "date",
                    },
                    "guests": {"title": "Guests", "type": "integer"},
                },
                "required": [
                    "hotel_id",
                    "guest_name",
                    "checkin_date",
                    "checkout_date",
                    "guests",
                ],
            },
        },
        {
            "name": "calc_reservation_price",
            "description": "calc_reservation_price(hotel_id: int, checkin_date: datetime.date, checkout_date: datetime.date, guests: int) - Useful to calculate the price of a reservation.",
            "parameters": {
                "title": "calc_reservation_priceSchemaSchema",
                "type": "object",
                "properties": {
                    "hotel_id": {"title": "Hotel Id", "type": "integer"},
                    "checkin_date": {
                        "title": "Checkin Date",
                        "type": "string",
                        "format": "date",
                    },
                    "checkout_date": {
                        "title": "Checkout Date",
                        "type": "string",
                        "format": "date",
                    },
                    "guests": {"title": "Guests", "type": "integer"},
                },
                "required": ["hotel_id", "checkin_date", "checkout_date", "guests"],
            },
        },
    ],
    "n": 1,
    "stream": True,
    "temperature": 0.0,
}

stream = client.chat.completions.create(**message)

for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")
