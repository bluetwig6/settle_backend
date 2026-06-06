import abc
# from collections.abc import Collection
from app.models import ContributionResponse, Expense, User
from sqlmodel import Session

class IContributionRepository(abc.ABC):
    """User repository interface."""

    @abc.abstractmethod
    async def add(self, session: Session, amount: int, expense: Expense, contributor: User ) -> ContributionResponse: ...

    @abc.abstractmethod
    async def delete(self, session: Session, id: int) -> None: ...
    
    @abc.abstractmethod
    async def get_by_id_or_none(self, session: Session, id: int) -> ContributionResponse|None: ...