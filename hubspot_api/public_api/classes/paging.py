from dataclasses import dataclass, field

@dataclass
class PagingNext:
    after: str
    link: str

@dataclass
class Paging:
    next: PagingNext

    @staticmethod
    def from_dict(data: dict):
        if data is None:
            return Paging(
                next=None
            )
        return Paging(
            next=PagingNext(
                after=data["next"]["after"],
                link=data["next"]["link"],
            )
        )
