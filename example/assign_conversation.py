from hubspot_api import HubSpotApi
import os

from dotenv import load_dotenv
load_dotenv()

def cb_auth() -> str:
    code = input('Enter 2FA code: ')
    return code

hs = HubSpotApi(os.getenv("HS_EMAIL"), os.getenv("HS_PASSWORD"), cb_auth)

# Assignees / Agents inside the company that you can assign tickets to
assignees = hs.conversations.get_assignees()

threads = hs.conversations.get_unassigned_threads()
if 0 < len(threads):
    johnDoe = assignees.find("John Doe")
    threads[0].assign(johnDoe)
