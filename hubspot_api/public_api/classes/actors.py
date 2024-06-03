from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional

@dataclass
class Actor:
    id: str
    type: str
    name: Optional[str] = None
    avatar: Optional[str] = None
    email: Optional[str] = None  # Since email is not present for all entities

@dataclass
class Actors:
    status: str
    startedAt: datetime
    completedAt: datetime
    results: List[Actor] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Actors':
        results = [Actor(**item) for item in data.get('results', [])]
        started_at = datetime.fromisoformat(data['startedAt'][:-1])  # Removing 'Z' before parsing
        completed_at = datetime.fromisoformat(data['completedAt'][:-1])  # Same here
        return cls(status=data['status'], results=results, startedAt=started_at, completedAt=completed_at)
