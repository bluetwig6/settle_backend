import abc
# from collections.abc import Collection
from typing import Any
from app.models import UserCreate, User, Group
from sqlmodel import Session

class IUserRepository(abc.ABC):
    """User repository interface."""

    @abc.abstractmethod
    async def add(self, session: Any, create_item:UserCreate ) -> User: ...

    @abc.abstractmethod
    async def get_users_by_username(self, session: Any, search_query:str ) -> list[User]: ...

    @abc.abstractmethod
    async def get_by_username_or_none(
        self, session: Any, username: str
    ) -> User | None: ...

    @abc.abstractmethod
    async def get_by_id(self, session: Session, id: int) -> User |None: ...
    
    @abc.abstractmethod
    async def get_multiple_by_id(self, session: Session, ids: list[int]) -> list[User]: ...

    @abc.abstractmethod
    async def get_groups(self, session: Session, user: User) -> list[Group]: ...

    @abc.abstractmethod
    async def remove_from_group(self, session: Session, group: Group, user: User ) -> None: ...
  
    @abc.abstractmethod
    async def add_to_group(self, session: Session, group: Group, user: User ) -> User: ...


    # @abc.abstractmethod
    # async def get_or_none(self, session: Any, user_id: int) -> UserDTO | None: ...

    # @abc.abstractmethod
    # async def get(self, session: Any, user_id: int) -> UserDTO: ...

    # @abc.abstractmethod
    # async def get_by_email_or_none(
    #     self, session: Any, email: str
    # ) -> UserDTO | None: ...

    # @abc.abstractmethod
    # async def get_by_email(self, session: Any, email: str) -> UserDTO: ...

    # @abc.abstractmethod
    # async def list_by_users(
    #     self, session: Any, user_ids: Collection[int]
    # ) -> list[UserDTO]: ...


    # @abc.abstractmethod
    # async def get_by_username(self, session: Any, username: str) -> UserDTO: ...

    # @abc.abstractmethod
    # async def update(
    #     self, session: Any, user_id: int, update_item: UpdateUserRecordDTO
    # ) -> UserDTO: ...
