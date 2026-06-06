import abc
# from collections.abc import Collection
from app.models import User, Expense, Item
from sqlmodel import Session

class IItemRepository(abc.ABC):
    """User repository interface."""

    @abc.abstractmethod
    async def add(self, session: Session, amount: int, title:str, expense:Expense, users: list[User] ) -> Item: ...

    @abc.abstractmethod
    async def delete(self, session: Session, id: int) -> None: ...
    
    @abc.abstractmethod
    async def get_by_id_or_none(self, session: Session, id: int) -> Item|None: ...