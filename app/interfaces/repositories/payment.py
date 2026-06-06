import abc
# from collections.abc import Collection
from app.models import Group, PaymentResponse, User
from sqlmodel import Session

class IPaymentRepository(abc.ABC):
    """User repository interface."""

    @abc.abstractmethod
    async def add(self, session: Session, amount: int, group: Group, payer: User, payee: User ) -> PaymentResponse: ...

    @abc.abstractmethod
    async def delete(self, session: Session, id: int) -> None: ...
    
    @abc.abstractmethod
    async def get_by_id_or_none(self, session: Session, id: int) -> PaymentResponse|None: ...