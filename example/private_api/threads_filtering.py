from hubspot_api import PrivateApi
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

"""
A more advance read_threads.py, which includes filtering and offset handling.
If above 100 threads are found, it will fetch the next 100 threads, and so on.
"""

def cb_auth() -> str:
    code = input('Enter 2FA code: ')
    return code

hs = PrivateApi(os.getenv("HS_EMAIL"), os.getenv("HS_PASSWORD"), cb_auth)
agents = hs.conversations.get_agents()

while hs.conversations.has_more():
    # Get all threads assigned to John Doe that have the latest message either on 2024-01-01 or 2024-01-02 (before 2024-01-03 0:00)
    threads = hs.conversations.get_threads(
        status=["STARTED", "ENDED"], # Both opened and closed threads
        agent=agents.find('John Doe'), # Only threads assigned to John
        start=datetime(2024,1,1), # Only threads with latest msg after 2024-01-01 0:00
        end=datetime(2024,1,3), # Only threads with latest msg before 2024-01-03 0:00
        search_query=None, # We could filter by search query
        )

    for thread in threads:
        print(thread.id, thread.subject, thread.status)

    if hs.conversations.has_more():
        print('\nFetching additional threads...\n')
        import time
        time.sleep(3.3) # Don't spam their API