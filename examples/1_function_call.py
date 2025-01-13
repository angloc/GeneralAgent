# Function Call
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
    handlers=[logging.StreamHandler()],
)
from GeneralAgent import Agent
from dotenv import load_dotenv

load_dotenv()


# Function: Get weather information
def get_weather(city: str) -> str:
    """
    get weather information
    @city: str, city name
    @return: str, weather information
    """
    # return f"{city} weather: sunny"
    weather = "sunny"
    print(f"{city} weather: {weather}")
    return weather


# agent = Agent('You are a weather assistant', functions=[get_weather], model='deepseek-chat')
agent = Agent("You are a weather assistant", functions=[get_weather])
agent.user_input("How's the weather in Chengdu?")

# Output
# ```python
# city = "Chengdu"
# weather_info = get_weather(city)
# weather_info
# ```
# The weather in Chengdu is sunny.
# Is there anything else I can help you with?
