# Verify generated content when using agent.run command
from GeneralAgent import Agent
from GeneralAgent import skills
from dotenv import load_dotenv

load_dotenv()

# Step 0: Define Agent
agent = Agent('You are a novelist')

# Step 1: Get novel name and theme from user
# topic = skills.input('Please enter the novel name and theme: ')
topic = 'The story of a bunny who eats candy without brushing teeth'

# Step 2: Novel summary
summary = agent.run(f'The novel name and theme is: {topic}, please expand and refine the novel summary. It should be artistic, educational, and entertaining.')

# Step 3: Generate chapter names and summaries list
chapters = agent.run('Output the novel chapter names and summaries for each chapter, return as list [(chapter_title, chapter_summary), ....]', return_type=list, user_check=True)

# Step 4: Generate detailed content for each chapter
agent.disable_python()
contents = []
for index, (chapter_title, chapter_summary) in enumerate(chapters):
    content = agent.run(f'For chapter: {chapter_title}\nSummary: {chapter_summary}. \nWrite detailed content for this chapter, return content only without title.')
    content = '\n'.join([x.strip() for x in content.split('\n')])
    contents.append(content)

# Step 5: Format and write novel to file
with open('novel.md', 'w') as f:
    for index in range(len(chapters)):
        f.write(f'### {chapters[index][0]}\n')
        f.write(f'{contents[index]}\n\n')

# Step 6 (Optional): Convert markdown file to pdf

# Step 7: Output novel file to user
skills.output('Your novel has been generated: [novel.md](novel.md)\n')
