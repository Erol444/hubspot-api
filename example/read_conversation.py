from hubspot_api import HubSpotApi
import os

from dotenv import load_dotenv
load_dotenv()

def cb_auth() -> str:
    code = input('Enter 2FA code: ')
    return code

hs = HubSpotApi(os.getenv("HS_EMAIL"), os.getenv("HS_PASSWORD"), cb_auth)

# You can also do hs.conversations.get_threads() to get all threads
threads = hs.conversations.get_threads()

if len(threads) == 0:
    raise Exception('No Conversation threads found!')

messages = threads[0].read_messages()
print(f"Thread subject {threads[0].subject}\n")

for i, msg in enumerate(messages):
    # Older messages are at the back (higher i num)
    print(f"----------\n{i}. message from {msg.fromEmail} at {msg.timestamp}, to {msg.to}, cc-ed {msg.cc}, text: \n{msg.text}")
