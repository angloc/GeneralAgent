# Using Doubao Large Language Model
# To use Doubao model, first install the library: pip install 'volcengine-python-sdk[ark]'
# Set model to doubao to distinguish from volcengine LLM connection library
# Since Doubao's interface model is Endpoint, use base_url to specify the Endpoint (which model)

from GeneralAgent import Agent
from dotenv import load_dotenv

load_dotenv()

api_key = 'your_api_key'
endpoint = 'your_endpoint_id'
agent = Agent('You are a helpful assistant', model='doubao', api_key=api_key, base_url=endpoint)
agent.user_input('Tell me about Chengdu')
