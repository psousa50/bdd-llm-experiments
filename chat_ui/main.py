import gradio as gr
import requests


def predict(message, history):
    response = requests.get("http://localhost:8000/chat/", params={"query": message})
    response = response.json()
    return response["message"]


gr.ChatInterface(predict).launch()
