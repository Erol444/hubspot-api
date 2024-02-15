from typing import Dict, List

class Agent:
    """
    An agent inside your company that you can assign tickets to
    """
    def __init__(self, raw: Dict):
        self.portalId = raw['portalId']
        self.userId = raw['userId']
        self.email = raw['email']
        self.firstName = raw['firstName']
        self.lastName = raw['lastName']
        self.avatar = raw['avatar']
        self.agentType = raw['agentType']
        self.assignable = raw['assignable']
        self.activeAccount = raw['activeAccount']
        self.agentState = raw['agentState']
        self.salesPro = raw['salesPro']
        self.activationStatus = raw['activationStatus']

    # Override str
    def __str__(self):
        name = f"{self.firstName} {self.lastName}"
        return f'<strong data-at-mention data-user-id="{self.userId}" data-search-text="{name}" data-search-value="{self.email}">@{name}</strong>'

class Agents:
    """
    List of Agents (possible assignees) inside your company that you can assign tickets to
    """
    def __init__(self, agents: Dict):
        self.list = [Agent(a) for a in agents['results']]

    def find(self, agent: str) -> Agent:
        """
        Pass either Name+Surname, or the email of the assignee
        """
        for a in self.list:
            if a.email == agent:
                return a
            if f'{a.firstName} {a.lastName}' == agent:
                return a
        return None