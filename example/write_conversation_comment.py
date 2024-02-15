from hubspot_api import HubSpotApi
import os

from dotenv import load_dotenv
load_dotenv()

def cb_auth() -> str:
    code = input('Enter 2FA code: ')
    return code

hs = HubSpotApi(os.getenv("HS_EMAIL"), os.getenv("HS_PASSWORD"), cb_auth)

# Assignees / Agents inside the company that you can assign tickets to
agents = hs.conversations.get_agents()
threads = hs.conversations.get_threads()

if len(threads) == 0:
    raise Exception('No Conversation threads found!')

thread = threads[0]
thread.comment('Hello, this is a test comment')

# Tagging an agent is also supported
agent = agents.find('John Doe')
thread.comment(f'Hi {agent}, could you please look into this?')
