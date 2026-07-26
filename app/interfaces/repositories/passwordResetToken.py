import abc
from datetime import datetime
from typing import List
# from collections.abc import Collection
from app.models import PasswordResetToken
from sqlmodel import Session

class IPasswordResetTokenRepository(abc.ABC):
    """User repository interface."""

    @abc.abstractmethod
    async def save_token_hash(self, session: Session, user_id: int, token_hash: str, expiration_time: datetime ) -> PasswordResetToken: ...
    
    @abc.abstractmethod
    async def get_token_object_by_hash_or_none(self, session: Session, token_hash:str) -> PasswordResetToken|None: ...
    
    @abc.abstractmethod
    async def get_all_tokens_for_user_id(self, session: Session, user_id: int) -> List[PasswordResetToken]: ...
    
    @abc.abstractmethod
    async def delete_all_existing_tokens_for_user_id(self, session: Session, user_id: int) -> None:...
    
    @abc.abstractmethod
    async def delete_token_by_hash(self, session: Session, token_hash: str) -> bool:...
    