from unittest.mock import Mock

from langchain_community.tools.file_management import (
    ReadFileTool,
    WriteFileTool,
    ListDirectoryTool,
)

from file_assistant.assistant import FileAssistant, FileAssistantDependencies

verbose = True


def mock_langchain_tool(tool, mock=None):
    if mock is None:
        mock = Mock()
    tool.__dict__["_run"] = mock
    return tool


def test_write_file():
    dependencies = FileAssistantDependencies(
        read_file=mock_langchain_tool(ReadFileTool()),
        write_file=mock_langchain_tool(WriteFileTool()),
        list_directory=mock_langchain_tool(ListDirectoryTool()),
    )

    file_assistant = FileAssistant(dependencies=dependencies, verbose=verbose)

    query = "Write 'This is foo content' to file 'foo.txt'"
    file_assistant.invoke(query)

    dependencies.write_file._run.assert_called_once_with(
        file_path="foo.txt", text="This is foo content"
    )


def test_file_foo_does_not_exist():
    dependencies = FileAssistantDependencies(
        read_file=mock_langchain_tool(ReadFileTool()),
        write_file=mock_langchain_tool(WriteFileTool()),
        list_directory=mock_langchain_tool(
            ListDirectoryTool(), Mock(return_value="No files found")
        ),
    )

    file_assistant = FileAssistant(dependencies=dependencies, verbose=verbose)

    query = "If a file named 'foo.txt' exists, read it and write a file named 'bar.txt' with the contents, else write 'This is foo content' to file 'foo.txt'"  # noqa E501
    file_assistant.invoke(query)

    dependencies.list_directory._run.assert_called_once_with(dir_path=".")
    dependencies.write_file._run.assert_called_once_with(
        file_path="foo.txt", text="This is foo content"
    )


def test_file_foo_exists():
    dependencies = FileAssistantDependencies(
        read_file=mock_langchain_tool(
            ReadFileTool(), Mock(return_value="This is foo content")
        ),
        write_file=mock_langchain_tool(WriteFileTool()),
        list_directory=mock_langchain_tool(
            ListDirectoryTool(), Mock(return_value="Files: 1. foo.txt")
        ),
    )

    file_assistant = FileAssistant(dependencies=dependencies, verbose=verbose)

    query = "If a file named 'foo.txt' exists, read it and write a file named 'bar.txt' with the contents, else write 'This is foo content' to file 'foo.txt'"  # noqa E501
    file_assistant.invoke(query)

    dependencies.list_directory._run.assert_called_once_with(dir_path=".")
    dependencies.read_file._run.assert_called_once_with(file_path="foo.txt")
    dependencies.write_file._run.assert_called_once_with(
        file_path="bar.txt", text="This is foo content"
    )
