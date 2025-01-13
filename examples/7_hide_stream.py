# Hide output stream from user display
from GeneralAgent import Agent
from dotenv import load_dotenv

load_dotenv()

agent = Agent('You are a helpful agent.', model='gpt-3.5-turbo')
chengdu_description = agent.run('Tell me about Chengdu', display=True)
print(chengdu_description)
