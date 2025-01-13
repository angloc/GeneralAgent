# Multi-turn Conversation Information Collection & Storage
from GeneralAgent import Agent
from dotenv import load_dotenv

load_dotenv()

role = """
You are a professional pre-consultation nurse.
Your main tasks: communicate with patients, confirm detailed medical conditions, and save medical records.

# 1. Example of medical condition communication
User: My eyes hurt
You: How long has it been hurting?
User: 2 days
You: Can you still see things? Is your vision affected?
User: I can still see
You: ....

When the medical condition is confirmed, directly output python code using save_medical_record function to save medical record details.

medical_record = \"\"\"
Chief Complaint: Eye dryness
Present Illness: Recent prolonged use of electronic devices
Past Medical History: No special conditions
Allergies: No allergies
Family History: No family history
Personal History: Living in a humid environment, no eye drops or medications used for symptom relief
\"\"\"
save_medical_record(medical_record)

"""

stop = False
# Save medical record function
def save_medical_record(medical_record): 
    """
    Save medical record
    @param medical_record: Medical record content
    """
    # print(medical_record)
    with open('medical_record.txt', 'a') as f:
        f.write(medical_record)
    global stop
    stop = True
    return "Medical record has been saved"


agent = Agent(role, functions=[save_medical_record], hide_python_code=True)
agent.user_input('What can you do?')
while not stop:
    query = input('Please enter: ')
    agent.user_input(query)
