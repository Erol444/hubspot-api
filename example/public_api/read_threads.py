from hubspot_api import Api
import os
from dotenv import load_dotenv
load_dotenv()

hs = Api(os.getenv("HS_API_KEY"))

while hs.conversations.has_more():
    threads = hs.conversations.get_threads(minute_threshold=60*24*30)
    for t in threads:
        print(f"[{t.latestMessageTimestamp.strftime('%Y-%m-%d %H:%M:%S')}] ID: {t.id}, Status {t.status}, Assigned to: {t.assignedTo}, Associated Contact: {t.associatedContactId}")

