from hubspot_api import PrivateApi
import os

from dotenv import load_dotenv
load_dotenv()

def cb_auth() -> str:
    code = input('Enter 2FA code: ')
    return code

hs = PrivateApi(os.getenv("HS_EMAIL"), os.getenv("HS_PASSWORD"), cb_auth)

# Assignees / Agents inside the company that you can assign tickets to
agents = hs.conversations.get_agents()

threads = hs.conversations.get_unassigned_threads()
if 0 < len(threads):
    johnDoe = agents.find("John Doe")
    threads[0].assign(johnDoe)
