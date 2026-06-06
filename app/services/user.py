from typing import Any

from sqlmodel import Session

from app.interfaces.services.user import IUserService
from app.interfaces.repositories.user import IUserRepository
from app.interfaces.repositories.group import IGroupRepository
from app.models import Group, User, UserBase, UserCreate

from fastapi import HTTPException, status
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError

class UserService(IUserService):
  """Service to handle user related logic"""

  def __init__(self, user_repo: IUserRepository, group_repo: IGroupRepository) -> None:
    self._user_repo = user_repo
    self._group_repo = group_repo

  async def create_user(self, session: Any, user_to_create: UserCreate) -> UserBase:
    try:
        user = await self._user_repo.add(session=session, create_item=user_to_create)
        return user
    except IntegrityError as e: 
      assert isinstance(e.orig, UniqueViolation)
      message =e.orig.diag.message_detail
      raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail= message
      )
    
  async def search_users(self, session: Any, search_query: str) -> list[User]:
    user_list = await self._user_repo.get_users_by_username(
      session=session,
      search_query=search_query
    )
    return user_list

  async def get_user_by_username(self, session: Any, username: str) -> User | None:
    return await self._user_repo.get_by_username_or_none(session, username)
  
  async def get_user_groups(self, session: Session, user: User) -> list[Group]:
    return user.groups
  
  async def remove_user_from_group(self, session: Session, current_user: User, group_id: int, user_id: int) -> None:
    group = await self._group_repo.get_by_id_or_none(session, id=group_id)
    user = await self._user_repo.get_by_id(session, id=user_id)
    if (not group) or (not user):
      raise HTTPException(
          status_code=status.HTTP_409_CONFLICT,
          detail= "User or Group not found"
      )
      
    if(current_user in group.users):
        if(not user in group.users):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail= "User is not in group"
            )       
        await self._user_repo.remove_from_group(session, group, user)
        return None
    else:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You cannot perform this action",
            headers={"WWW-Authenticate": "Bearer"},
        )
        raise(credentials_exception)
  
  async def add_user_to_group(self, session: Session, current_user: User, group_id: int, user_id: int) -> User:
    group = await self._group_repo.get_by_id_or_none(session=session, id=group_id)
    user = await self._user_repo.get_by_id(session=session, id=user_id)
    if (not group) or (not user):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail= "User or Group not found"
        )
    
    if(current_user in group.users):
        if(user in group.users):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail= "User is already in group"
            )       
        updated_user = await self._user_repo.add_to_group(session, group, user)
        return updated_user
    else:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You cannot perform this action",
            headers={"WWW-Authenticate": "Bearer"},
        )
        raise(credentials_exception)