from hubspot_api import Api
from hubspot_api.public_api.classes.thread import Thread
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
load_dotenv()

hs = Api(os.getenv("HS_API_KEY"))

ts = datetime.now(timezone.utc) - timedelta(days=30)

while hs.conversations.has_more():
    threads = hs.conversations.get_threads(timestamp=ts)
    for t in threads:
        t: Thread
        msgs = t.read_messages(oldest_first=True)
        if len(msgs) == 0:
            continue
        print(f"Thread {t.id} has history")
        print(msgs[0].get_text())
        if msgs[0].has_history():
            print('1st msg has history!')
            print('\n-------\n')
            richText = msgs[0].get_history()
            # Save into a file
            with open(f'{t.id}.html', 'w') as f:
                f.write(richText)
            exit(0)

