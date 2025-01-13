# AI Search
# Prerequisites: 
# 1. Configure environment variable SERPER_API_KEY (API KEY from https://serper.dev/);
# 2. Install selenium library: pip install selenium

from GeneralAgent import Agent
from GeneralAgent import skills
from dotenv import load_dotenv

load_dotenv()
google_results = []

# Step 1: First Google search
question = input('Please enter your question for AI search: ')
# question = 'Zhou Hongyi selling cars'
content1 = skills.google_search(question)
google_results.append(content1)

# Step 2: Second Google search: Get follow-up search queries based on first search results
agent = Agent('You are an AI search assistant.')
querys = agent.run(f'User question: \n{question}\n\nSearch engine results: \n{content1}\n\nWhat key phrases should we search next to help the user (max 3, and not too similar to the original question)? Return a list variable of key phrases ([query1, query2])', return_type=list)
print(querys)
for query in querys:
    content = skills.google_search(query)
    google_results.append(content)

# Step 3: Extract important webpage content
agent.clear()
web_contents = []
google_result = '\n\n'.join(google_results)
urls = agent.run(f'User question: \n{question}\n\nSearch engine results: \n{google_result}\n\nWhich webpages are most helpful for the user question? Please return a list variable of the most important URLs (max 5) ([url1, url2, ...])', return_type=list)
for url in urls:
    print(url)
    content = skills.web_get_text(url, wait_time=2)
    web_contents.append(content)

# Step 4: Output results
agent.clear()
web_content = '\n\n'.join(web_contents)
agent.run(f'User question: \n{question}\n\nSearch engine results: \n{google_result}\n\nSelected webpage content: \n{web_content}\n\nBased on the user question, search engine results, and webpage content, please provide a detailed answer organized in a directory structure using markdown format.')
