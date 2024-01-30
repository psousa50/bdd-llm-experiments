from fastapi import FastAPI
from hotel_reservations.assistant import HotelReservationsAssistant

app = FastAPI()

assistant = HotelReservationsAssistant(verbose=True)


@app.get("/hello/")
async def hello():
    return {"message": "Hello World"}


@app.get("/chat/")
async def chat(query: str):
    response = assistant.invoke(query)
    return {"message": response["output"]}
