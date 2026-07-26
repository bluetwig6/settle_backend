import abc
from app.models import UserCreate, UserBase
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import Depends
from app.models import Token
from sqlmodel import Session

# from collections.abc import Collection

class IUserAuthService(abc.ABC):

  @abc.abstractmethod
  async def sign_in_user(self,session:Session, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token: ...

  @abc.abstractmethod
  async def sign_up_user(self,session:Session, user:UserCreate) -> UserBase: ...
  
  @abc.abstractmethod
  async def send_reset_password_email(self, session:Session, email: str, ) -> bool: ...
  
  @abc.abstractmethod
  async def reset_password(self, session: Session, token: str, new_password: str) -> bool: ...