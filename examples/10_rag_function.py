from dotenv import load_dotenv

load_dotenv()
# RAG function

# Set log level
import os
os.environ['AGENT_LOG'] = 'debug'

from GeneralAgent import Agent

def rag_function(messages):
    input = messages[-1]['content']
    print('user input:', input)
    # TODO: Return relevant background knowledge based on input or more information from messages
    return 'Background: GeneralAgent is a Python library for building AI assistants. It provides a simple API for building conversational agents.'

agent = Agent('You are a helpful assistant', rag_function=rag_function)
agent.user_input('What is GeneralAgent?')
