
import openai
import time
from dotenv import load_dotenv
api_key = ''
client = openai.Client(api_key=api_key)
dataPath = '1.pdf'
# Step 1: Create an Assistant
file = client.files.create(file=open("1.pdf", "rb"), purpose="assistants")

# Step 2. Create the Assistant
assistant = client.beta.assistants.create(
    instructions="You are a chatbot for Bean There Café, and you have access to files to answer questions about the company.",
    name="Bean There Café Bot",
    tools=[{"type": "retrieval"}],
    model="gpt-4-1106-preview",
    file_ids=[file.id],
)
print(assistant)

# Step 2: Create a Thread
thread = client.beta.threads.create()

# Step 3: Add a Message to a Thread
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content='''Identify critical clauses such as:
 Termination causes.
 High-value clauses.
 Potential exceptions (e.g., ambiguous terms, non-standard clauses).
    ''',
)

# Step 4: Run the Assistant
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
    instructions="Please provide the exact contents which I uploaded"
)

# Waits for the run to be completed. In actual production, you may want to use a webhook instead.
while True:
    run_status = client.beta.threads.runs.retrieve(thread_id=thread.id, 
                                                   run_id=run.id)
    if run_status.status == "completed":
        break
    elif run_status.status == "failed":
        print("Run failed:", run_status.last_error)
        break
    time.sleep(2)  # wait for 2 seconds before checking again


# Step 5: Parse the Assistant's Response and Print the Results
messages = client.beta.threads.messages.list(
    thread_id=thread.id
)

# Prints the messages the latest message the bottom
number_of_messages = len(messages.data)
print( f'Number of messages: {number_of_messages}')

for message in reversed(messages.data):
    role = message.role  
    for content in message.content:
        if content.type == 'text':
            response = content.text.value 
            print(f'\n{role}: {response}')