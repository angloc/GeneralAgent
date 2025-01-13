# Multiple Agents Working Together
from GeneralAgent import Agent
from dotenv import load_dotenv

load_dotenv()
story_writer = Agent('You are a story writer who creates detailed story content based on outlines or story concepts.')
humor_enhancer = Agent('You are a story polisher who adds humor and wit to stories. Output the polished story directly.')

# Disable Python execution
story_writer.disable_python_run = True
humor_enhancer.disable_python_run = True

# topic = skills.input('Please enter the story outline or concept: ')
topic = 'Write a story about a little white rabbit who eats candy without brushing teeth, make it educational.'
initial_story = story_writer.run(topic)
enhanced_story = humor_enhancer.run(initial_story)
print(enhanced_story)
