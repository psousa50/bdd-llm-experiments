from hotel_reservations.assistant import HotelReservationsAssistant


def start():
    assistant = HotelReservationsAssistant()
    query = "I want to book a room"
    response = assistant.invoke(query)
    print(response)
    query = "I want to book a room in London, starting in May 2 and ending in May 7, for 3 guests"
    response = assistant.invoke(query)
    print(response)
    query = "I want to book Hotel UK 2"
    response = assistant.invoke(query)
    print(response)


if __name__ == "__main__":
    start()
