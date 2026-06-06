import abc
from typing import Any
from app.models import UserCreate, UserBase, User, Group
from sqlmodel import Session
# from collections.abc import Collection

class IUserService(abc.ABC):

  @abc.abstractmethod
  async def create_user(self,session:Any, user_to_create:UserCreate) -> UserBase: ...

  @abc.abstractmethod
  async def search_users(self,session:Any, search_query:str) -> list[User]: ...

  @abc.abstractmethod
  async def get_user_by_username(self, session: Any, username: str) -> User | None: ...

  @abc.abstractmethod
  async def get_user_groups(self, session: Session, user: User ) -> list[Group]: ...

  @abc.abstractmethod
  async def remove_user_from_group(self, session: Session, current_user: User, group_id: int, user_id: int ) -> None: ...

  @abc.abstractmethod
  async def add_user_to_group(self, session: Session, current_user: User, group_id: int, user_id: int ) -> User: ...

  # @abc.abstractmethod
  # async def get_users_by_ids(
  # self, session: Any, user_ids: Collection[int]
  # ) -> list[UserBase]: ...

  # @abc.abstractmethod
  # async def get_user_by_id(self, session: Any, user_id: int) -> UserBase: ...

  # @abc.abstractmethod
  # async def get_user_by_email(self, session: Any, email: str) -> UserBase: ...



  # @abc.abstractmethod
  # async def update_user(
  # self, session: Any, current_user: User, user_to_update: User
  # ) -> UpdatedUserDTO: ...