from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class Agent:
    id: str
    email: str
    type: str
    firstName: str
    lastName: str
    userId: int
    userIdIncludingInactive: int
    createdAt: str
    updatedAt: str
    archived: bool
    teams: Optional[Any] = None  # Set default to None

@dataclass
class Agents:
    list: List[Agent] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Agents':
        results = [Agent(**item) for item in data.get('results', [])]
        return cls(list=results)

    def find(self, agent: str) -> Agent:
        """
        Pass either Name+Surname, or the email of the assignee
        """
        for a in self.list:
            if a.id == agent or \
                str(a.userId) == agent or \
                str(a.userId) == agent.replace('A-', '') or \
                a.email == agent or \
                f'{a.firstName} {a.lastName}' == agent:
                return a
        return None

