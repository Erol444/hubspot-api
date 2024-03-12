import requests
import json
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, List
from .api_client import ApiClient
from .classes.thread import Thread
from .classes.threads import Threads
from .classes.agents import Agents

class Conversations:
    def __init__(self, api: ApiClient):
        self.api = api
        self.after: Optional[str] = None
        self.agents: Dict = None

    def get_inboxes(self) -> dict:
        """
        returns:
            {"total":1,"results":[{"id":"74281021","name":"Inbox","createdAt":"2021-11-23T11:32:14.501Z","updatedAt":"2023-05-11T20:01:05.259Z"}]}
        """
        url = "/conversations/v3/conversations/inboxes"
        json_text = self.send_request(url, "GET").text
        # Decode json
        return json.loads(json_text)

    def has_more(self) -> bool:
        """
        Check if there are more threads available. Can be used with `while convo.has_more(): threads = convo.get_threads()`
        """
        return self.after is not False


    def get_threads(self, inboxId:str=None, timestamp: datetime = None) -> List[Thread]:
        """
        Get conversation threads. First thread in the list is the oldest one, last one is the newest one.

        Args:
            timestamp (timedelta): Get threads after this timestamp. Note that is should be UTC timezone! Default is 60 minutes ago.
        """
        if timestamp is None:
            timestamp = datetime.now(timezone.utc) - timedelta(minutes=60)

        # In format of 2024-03-11T15:06:22.889Z
        params = {
            'sort':'latestMessageTimestamp',
            'latestMessageTimestampAfter': timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            'limit': 50
        }
        # ts = datetime.now(timezone.utc) - timedelta(minutes=minute_threshold)
        # params = {
        #     'sort':'latestMessageTimestamp',
        #     'latestMessageTimestampAfter':ts.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        #     'limit': 50
        # }
        if self.after:
            params['after'] = self.after
        if inboxId:
            params['inboxId'] = inboxId

        res = self.api.api_call("GET", "/conversations/v3/conversations/threads", params=params)
        print(res.data)

        threads = Threads.from_dict(res.data, self.api)

        if len(threads.results) == 50 and threads.paging.next.after:
            self.after = threads.paging.next.after
        else:
            self.after = False
        return threads.results

    def get_thread_by_id(self, id: int) -> Thread:
        """
        Get conversation thread by id
        """
        res = self.api.api_call("GET", f"/conversations/v3/conversations/threads/{id}")
        return Thread.from_dict(res.data, self.api)

    def get_agents(self, use_cached=True) -> Agents:
        """
        Get agents
        Args:
            use_cached (bool): Whether to use cached response of agents
        """
        # Check in agents.json
        if use_cached and self.agents is None:
            try:
                with open('agents.json', 'r') as f:
                    self.agents = json.load(f)
            except:
                self.agents = None

        if self.agents is None:
            res = self.api.api_call("GET", "/crm/v3/owners")
            self.agents = res.data
            # Save to agents.json
            with open('agents.json', 'w') as f:
                json.dump(self.agents, f)

        return Agents.from_dict(self.agents)

