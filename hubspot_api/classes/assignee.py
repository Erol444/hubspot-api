from typing import Dict, List

class Assignee:
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

class Assignees:
    """
    List of Assignees (Agents) inside your company that you can assign tickets to
    """
    def __init__(self, assignees: Dict):
        self.list = [Assignee(a) for a in assignees['results']]

    def find(self, assignee) -> Assignee:
        """
        Pass either Name+Surname, or the email of the assignee
        """
        for a in self.list:
            if a.email == assignee:
                return a
            if f'{a.firstName} {a.lastName}' == assignee:
                return a
        return None