from typing import Any

from sqlmodel import Session, select, col
from app.models import Group, UserCreate, User
from app.interfaces.repositories.user import IUserRepository
from app.services.password import get_password_hash

class UserRepository(IUserRepository):
  """ Repository for user model """

  async def add(
      self, session:Session, create_item: UserCreate
  ) -> User:
      hashed_password = get_password_hash(create_item.password)
      db_user = User(**create_item.model_dump(), hashed_password=hashed_password)
      session.add(db_user)
      session.commit()
      session.refresh(db_user)
      return db_user
  
  async def get_users_by_username(self, session: Any, search_query: str) -> list[User]:
    users = session.exec(select(User).filter(User.username.contains(search_query))).all() # type: ignore
    return users
  
  async def get_by_email_or_none(self, session: Session, email: str) -> User | None:
    user = session.exec(select(User).where(User.username == email)).first()
    if user:
      return user
    return None
  
  async def get_by_username_or_none(self, session: Session, username: str) -> User | None:
    user = session.exec(select(User).where(User.username == username)).first()
    if(user):
      return user
    return None
  
  async def get_by_id_or_none(self, session: Session, id: int) -> User | None:
    user = session.exec(select(User).where(User.id == id)).first()
    if(user):
      return user
    return None
  
  async def get_groups(self,session:Session, user: User) -> list[Group]:
    return user.groups
  
  async def add_to_group(self, session: Session, group: Group, user: User) -> User:
    user.groups.append(group)
    session.add(user)
    session.commit()
    return user
  
  async def remove_from_group(self, session: Session, group: Group, user: User) -> None:
    user.groups.remove(group)
    session.add(user)
    session.commit()
    return None
  
  async def get_multiple_by_id(self, session: Session, ids: list[int]) -> list[User]:
    users = session.exec(select(User).where(col(User.id).in_(ids))).all()
    return list(users)
  
  async def update_user(self, session: Session, user: User) -> User:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user