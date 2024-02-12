import json
import logging
from typing import List
from .api_client import ApiClient
from .classes.threads import Thread
from .classes.assignee import Assignees

class Conversations:
    def __init__(self, api_client: ApiClient):
        self.api = api_client

        self.inboxes = self.__put_inbox()
        self.inboxId = None
        self.assignees: Assignees = None

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

    def get_assignees(self) -> Assignees:
        if self.assignees is not None:
            return self.assignees

        response = self.api.api_call('GET',
            '/cv/inbox/settings/v1/assignee-search',
            params={
                'workspaceId': self.inboxId,
                'limit': 100,
                'offset': 0,
            }
        )
        assignees = json.loads(response.text)
        self.assignees = Assignees(assignees)
        return self.assignees

    def get_unassigned_threads(self) -> List[Thread]:
        threads = self.get_threads(status=["STARTED"])
        return list(filter(lambda t: t.assigned_agent == None, threads))

    def get_threads(self, status=["STARTED"]) -> List[Thread]:
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

        response = self.api.api_call(
            "PUT",
            f"/threadlists/v1/members",
            params={
                "expectedResponseType": "WRAPPER_V2",
                "historyLimit": 30,
                "membersLimit": 50,
            },
            data=data,
        )

        # with open('put_threadlist.json', 'w', encoding='utf-8') as file:
        #     file.write(response.text)

        data = json.loads(response.text)
        results = data["viewMemberPagedResult"]["results"]
        results.sort(key=lambda x: x["latestMessageTimestamp"], reverse=True)

        return [Thread(result, self.api) for result in results]

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
        # Save reponse.txt as utf-8
        inboxes = json.loads(response.text)["inboxes"]

        # with open('put_inbox.json', 'w', encoding='utf-8') as file:
        #     file.write(response.text)
        return inboxes
