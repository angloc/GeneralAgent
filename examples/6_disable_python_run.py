# Disable Python Run
# By default, GeneralAgent executes Python code input by users. If you don't want GeneralAgent to run Python code, you can disable Python execution by setting the `disable_python_run` property to `True`.
from GeneralAgent import Agent
from dotenv import load_dotenv

load_dotenv()

agent = Agent('You are a Python expert helping users solve Python problems.')
agent.disable_python_run = True
agent.user_input('Implement a function in Python to read a file')

# Here's a Python function to read file contents:

# ```python
# def read_file(file_path):
#     try:
#         with open(file_path, 'r', encoding='utf-8') as file:
#             content = file.read()
#         return content
#     except FileNotFoundError:
#         return "File not found."
#     except Exception as e:
#         return f"An error occurred: {e}"

# # Example usage
# file_content = read_file('example.txt')
# file_content
# ```

# This `read_file` function takes a file path as a parameter, attempts to read the file contents with UTF-8 encoding, and returns the content. If the file is not found or other errors occur, it returns the corresponding error message.
