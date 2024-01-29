from langchain_community.agent_toolkits import FileManagementToolkit

working_directory = "./tmp/working_directory"

tools = FileManagementToolkit(
    root_dir=str(working_directory),
    selected_tools=["read_file", "write_file", "list_directory"],
).get_tools()

print(type(tools))

for t in tools:
    print(type(t).__name__)
