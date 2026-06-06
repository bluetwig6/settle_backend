from app.interfaces.services.user import IUserService
from sqlmodel import Session
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status
from app.models import Token
from app.config import get_app_settings
from app.models import UserCreate, UserBase, User
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from app.interfaces.services.auth import IUserAuthService
from app.interfaces.services.auth_token import IAuthTokenService
from typing import Annotated
from app.services.password import get_password_hash, verify_password_hash

settings = get_app_settings()

class UserAuthService(IUserAuthService):
  """ Service to handle user auth """

  def __init__(
    self, 
    user_service: IUserService, 
    auth_token_service: IAuthTokenService
  ):
      self._user_service = user_service
      self._auth_token_service = auth_token_service


  async def sign_in_user(
    self,
    session: Session,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
  ) -> Token:
    user = await self._user_service.get_user_by_username(session, username=form_data.username)      
    if not user:
      raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
      )
    if not verify_password_hash(form_data.password,user.hashed_password):
      raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
      )
      
    jwt_token = self._auth_token_service.generate_jwt_token(user=user) 
    return jwt_token
  
  async def sign_up_user(
    self,
    session: Session,
    user: UserCreate
  ) -> UserBase:
    try:
        hashed_password = get_password_hash(user.password)
        db_user = User(**user.model_dump(), hashed_password=hashed_password)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user
    except IntegrityError as e: 
        assert isinstance(e.orig, UniqueViolation)
        message =e.orig.diag.message_detail
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail= message
        )