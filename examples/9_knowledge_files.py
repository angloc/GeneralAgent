# Knowledge Base
from GeneralAgent import Agent
from dotenv import load_dotenv

load_dotenv()

files = ['../docs/paper/General_Agent__Self_Call_And_Stack_Memory.pdf']
workspace = '9_knowledge_files'
agent = Agent('You are an AI assistant.', workspace=workspace, knowledge_files=files)
agent.user_input(['What does Self call mean?'])

# Clean up
import shutil
shutil.rmtree(workspace)


# Knowledge base by default uses the embedding_texts function in GeneralAgent.skills to embed text (default is OpenAI's text-embedding-3-small model)
# You can override the embedding_texts function to use other providers or local embedding methods, as follows:

# def new_embedding_texts(texts) -> [[float]]:
#     """
#     Perform embedding on an array of texts
#     """
#     # Your embedding method
#     return result
# from GeneralAgent import skills
# skills.embedding_texts = new_embedding_texts
