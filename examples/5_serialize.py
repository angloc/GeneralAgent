# Serialization
from GeneralAgent import Agent
from dotenv import load_dotenv

load_dotenv()

# Agent serialization location, automatically saves LLM messages and python interpreter state during runtime
workspace='./5_serialize'

role = 'You are a helpful agent.'
agent = Agent(role, workspace=workspace)
agent.user_input('My name is Shadow.')

agent = None
agent = Agent(role, workspace=workspace)
agent.user_input('What is my name?')

# Output: Your name is Shadow. How can I help you today, Shadow?

# agent: Clear memory + python serialization state
agent.clear()

agent.user_input('What is my name?')
# I'm sorry, but I don't have access to your personal information, including your name. How can I assist you today?

import shutil
shutil.rmtree(workspace)
