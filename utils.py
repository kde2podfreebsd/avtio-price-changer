import dataclasses
import enum 

class ItemStatus(enum.Enum):
    ACTIVE = "active"
    REMOVED = "removed"
    OLD = "old"
    BLOCKED = "blocked"
    REJECTED = "rejected"


@dataclasses.dataclass(frozen=True)
class Avitoitem:
    avito_id: int
    address: str
    category: str
    price: float
    status: ItemStatus
    title: str
    url: str 