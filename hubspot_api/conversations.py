import json
import logging
from typing import List
from .api_client import ApiClient
from .classes.threads import Thread
from .classes.agents import Agents, Agent
from datetime import datetime


class Conversations:
    def __init__(self, api_client: ApiClient):
        self.api = api_client

        self.inboxes = self.__put_inbox()
        self.inboxId = None
        self.agents: Agents = None

        self._search_offset = None

        if len(self.inboxes) == 0:
            raise Exception("No inboxes found")
        elif len(self.inboxes) == 1:
            self.inboxId = self.inboxes[0]["id"]
        else:
            logging.log(
                logging.INFO,
                "Multiple inboxes found, select with conversations.set_inbox(inboxId)",
            )

    def set_inbox(self, id: int):
        self.inboxId = self.inboxes[id]["id"]

    def get_agents(self) -> Agents:
        if self.agents is not None:
            return self.agents

        response = self.api.api_call('GET',
            '/cv/inbox/settings/v1/assignee-search',
            params={
                'workspaceId': self.inboxId,
                'limit': 100,
                'offset': 0,
            }
        )

        with open('agents.json', 'w', encoding='utf-8') as file:
            file.write(response.text)

        # TODO: if there are more agents, fetch the rest
        self.agents = Agents(response.data)
        return self.agents

    def get_unassigned_threads(self) -> List[Thread]:
        threads = self.get_threads(status=["STARTED"])
        return list(filter(lambda t: t.assigned_agent == None, threads))

    def get_threads(self, status=["STARTED"], agent: Agent = None, start: datetime = None, end: datetime = None, search_query: str = None) -> List[Thread]:
        """
        Get threads. First thread is the latest one, last one is the oldest one.

        If called multiple times, it will try to get the next page of threads (if available) - use has_more() to check if there are more threads.

        Args:
            status: Filter by thread status, options: ["STARTED", "ENDED", "SOFT_DELETED", "INITIALIZING"]
            agent: Filter by agent
            start: Only return threads that have latest message timestamp after this datetime
            end: Only return threads that have latest message before this datetime
            searchQuery: Search query, same as in HubSpot UI
        """
        data = {
            "inboxId": str(self.inboxId),
            "limit": 100,
            "maxPreviewLength": 200,
            "sortDirection": "DESC",
            "threadListId": 1,
            "threadListType": "DEFAULT",
        }
        if status is not None:
            data["threadStatus"] = status

        # Filters, use v2 API, it takes longer to respond
        if agent or start or end or search_query:
            if agent:
                data["assignment"] = { "agentId": agent.userId, "agentType": "HUMAN" }
            if start:
                data["startTimestamp"] = int(start.timestamp() * 1000)
            if end:
                data["endTimestamp"] = int(end.timestamp() * 1000)
            if search_query:
                data["searchQuery"] = search_query

            params = {}
            if self._search_offset:
                params['offsetTimestamp'] = self._search_offset['offsetTimestamp']
                params['offsetId'] = self._search_offset['offsetId']

            response = self.api.api_call(
                "PUT",
                "https://app-eu1.hubspot.com/api/messages/v2/threadlist/members/page",
                params=params,
                data=data
            )
            with open(f'threadslist1.json', 'w', encoding='utf-8') as file:
                file.write(response.text)
            results = response.data["pagedResult"]["results"]
            results.sort(key=lambda x: x["latestMessageTimestamp"], reverse=True)
        else: # No filters, use V1 API
            if self._search_offset:
                data["searchOffset"] = self._search_offset
            response = self.api.api_call(
                "PUT",
                f"/threadlists/v1/members",
                data=data,
            )
            results = response.data["viewMemberPagedResult"]["results"]
            results.sort(key=lambda x: x["latestMessageTimestamp"], reverse=True)

        # Has more
        if response.data['viewMemberPagedResult']['hasMore']:
            self._search_offset = response.data['viewMemberPagedResult']['offset']
        else:
            self._search_offset = False

        with open(f'threadslist.json', 'w', encoding='utf-8') as file:
            file.write(response.text)

        return [Thread(result, self.api) for result in results]

    def has_more(self) -> bool:
        """
        Check if there are more threads available. Can be used with `while convo.has_more(): threads = convo.get_threads()`
        """
        return self._search_offset is not False

    def __put_inbox(self):
        """
        Get available inboxes
        """
        response = self.api.api_call(
            "PUT",
            f"/messages/v2/inbox/omnibus",
            params={
                "expectedResponseType": "WRAPPER_V2",
                "historyLimit": 30,
                "membersLimit": 50,
            },
            data={
                "customViewId": None,
                "limit": 100,
                "sortDirection": "DESC",
                "threadList": None,
                "threadStatus": ["STARTED"],
            },
        )
        return response.data['inboxes']
