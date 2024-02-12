# HubSpot Private API

## Python library to interact with HubSpot's Private API

This is a Python library of HubSpot's Private API, which was reverse-engineered from their Mobile App. It allows users to do any kind of LLM automation / auto-reply (to live chats).

It was developed because **HubSpot doesn't bother making their Public API feature-complete**, and have had some modules in BETA for over a year (khm.. [Conversations](https://developers.hubspot.com/docs/api/conversations/conversations)).

**Additional features**, which their Public API doesn't support:

- Conversation: access Live Chat channels
- Conversation: Assign the conversation to an agent

## Demo script

```python
from hubspot_api import HubSpotApi

def cb_auth() -> str: # In case of 2FA, you'll need to return the code
    code = input('Enter 2FA code: ')
    return code

hs = HubSpotApi('my-email@provider.com', 'superSecretPw', cb_auth)

# You can also do hs.conversations.get_threads() to get all threads
threads = hs.conversations.get_unassigned_threads()
# Needed for assigning threads to agents
assignees = hs.conversations.get_assignees()

for t in threads:
    print('---------\nSubject:',t.subject, t.timestamp)
    msgs = t.read_messages()
    email_msgs = [f"FROM: {msg.fromName}, AT: {msg.timestamp}, EMAIL TEXT:\n{msg.text}" for msg in msgs]
    full_conversation = f'EMAIL SUBJECT: {t.subject}\n' + '\n\n'.join(email_msgs).lower()

    # Do some smart LLM stuff here

    if "api" in full_conversation or "code" in full_conversation:
        t.assign(assignees.find('John Doe')) # Tech support
    elif "shipping" in full_conversation:
        t.assign(assignees.find('Erik The Red')) # Ops/shipping
    elif "digital agency" in full_conversation:
        # They are trying to sell us something
        t.send_message("Thank you for your email, but we are not interested.")
        t.close()
    elif "tiktok" in full_conversation:
        t.spam() # TikTok? Spam for sure
```

## Module support

While HubSpot has many different modules (contacts, deals, tickets, etc.), most of them work as expected
with their [public API](). Only Conversations are in "BETA", and have been for over a year now.

## Installation

To install this Python package, run the following command:

```bash
pip install hubspot-api
```

### Liability

**Note:** This unofficial API library is not endorsed by HubSpot and likely violates their Terms of Service. Use it at your own risk; the creator assumes no liability for any consequences.