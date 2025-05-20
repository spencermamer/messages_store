from abc import ABC, abstractmethod
from typing import Optional, List

class NoticesStore(ABC):
    @abstractmethod
    def create_table(self):
        pass

    @abstractmethod
    def insert_notice(self, slug: str, notice: str):
        pass

    @abstractmethod
    def slug_exists(self, slug: str) -> bool:
        pass

    @abstractmethod
    def retrieve_notice(self, slug: str) -> Optional[str]:
        pass

    @abstractmethod
    def delete_notice(self, slug: str) -> bool:
        pass

    @abstractmethod
    def update_notice(self, slug: str, new_notice: str) -> bool:
        pass

    @abstractmethod
    def retrieve_all_notices(self) -> List[dict]:
        pass

    @abstractmethod
    def set_acknowledged_status(self, slug: str, acknowledged: int) -> bool:
        pass
