from dataclasses import dataclass
from hubspot_api.public_api.api_client import ApiClient
from .thread import Thread
from .paging import Paging

@dataclass
class Threads:
    results: list[Thread]
    paging: Paging

    @staticmethod
    def from_dict(data: dict, api: ApiClient):
        return Threads(
            results=[Thread.from_dict(x, api) for x in data.get("results")],
            paging=Paging.from_dict(data.get("paging")),
        )