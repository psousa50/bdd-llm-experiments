from file_assistant.assistant import FileAssistant


def start():
    file_assistant = FileAssistant(verbose=True)

    query = "If a file named 'foo.txt' exists, read it and write a file named 'bar.txt' with the contents, else write 'This is foo content' to file 'foo.txt'"  # noqa E501
    response = file_assistant.invoke(query)
    print(response["output"])


if __name__ == "__main__":
    start()
