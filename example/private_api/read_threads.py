from hubspot_api import PrivateApi
import os

from dotenv import load_dotenv
load_dotenv()

def cb_auth() -> str:
    code = input('Enter 2FA code: ')
    return code

hs = PrivateApi(os.getenv("HS_EMAIL"), os.getenv("HS_PASSWORD"), cb_auth)

threads = hs.conversations.get_threads()
for thread in threads:
    print("Thread subject:", thread.subject)
