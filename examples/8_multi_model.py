# Support other large language models through OpenAI Python SDK
# Or through https://github.com/songquanpeng/one-api to support other models
from GeneralAgent import Agent
from dotenv import load_dotenv

load_dotenv()

models = [
    ('deepseek-chat', 32000, 'sk-xxx', 'https://api.deepseek.com/v1'),  # Official DeepSeek support
    ('moonshot-v1-128k', 128000, '$MOONSHOT_API_KEY', 'https://api.moonshot.cn/v1'),  # Official Moonshot support
    ('SparkDesk-v3.5', 4000, None, None),
    ('glm-4v', 128000, None, None),
    ('ERNIE-4.0-8K', 8000, None, None),
    ('qwen-turbo', 6000, None, None),
    ('hunyuan', 8000, None, None),
]

for model, token_limit, api_key, base_url in models:
    agent = Agent('You are a helpful agent.', model=model, token_limit=token_limit, api_key=api_key, base_url=base_url)
    agent.user_input('Tell me about Chengdu')
