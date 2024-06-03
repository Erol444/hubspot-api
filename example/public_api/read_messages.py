from hubspot_api import Api
import os
from dotenv import load_dotenv
load_dotenv()

hs = Api(os.getenv("HS_API_KEY"))

threads = hs.conversations.get_threads(minute_threshold=60*3*20)
if len(threads) == 0:
    raise Exception('No threads found')

# Welcome, Comments, messages, re-assign messages, etc.
all_msgs = threads[0].read_all()

for msg in all_msgs:
    print(vars(msg))
    print('---')

