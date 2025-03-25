from hubspot_api import Api
from hubspot_api.public_api.classes.conversation import Conversation
from dotenv import load_dotenv
load_dotenv()
import json
import glob
from datetime import datetime, timedelta


files = glob.glob('threads/*.json')
total = 0
for file in files:
    with open(file, 'r') as f:
        data = json.load(f)
        msgs = data['all_messages']
        convo = Conversation.from_dict({'results': msgs, 'paging': {'next': {'after': '0', 'link': '0'}}}, None)

        # Only msgs
        all_msgs = convo.results
        msgs = list(filter(lambda x: x.type == 'MESSAGE', all_msgs))
        if len(msgs) < 2:
            continue
        
        for msg in msgs:
            if msg.createdBy.startswith('A-'):
                continue
            # Check if datetime is older than 150 days
            if msg.createdAt < datetime.now() - timedelta(days=150):
                continue

            total += 1

print(total)
