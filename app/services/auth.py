from datetime import datetime, timedelta, timezone
import hashlib
import secrets
from app.interfaces.repositories.passwordResetToken import IPasswordResetTokenRepository
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
    auth_token_service: IAuthTokenService,
    password_reset_token_repo: IPasswordResetTokenRepository
  ):
      self._user_service = user_service
      self._auth_token_service = auth_token_service
      self._password_reset_token_repo = password_reset_token_repo

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

  async def send_reset_password_email(
    self, 
    session: Session, 
    email: str,
    ) -> bool:

    user = await self._user_service.get_user_by_email(session,email)
    if not user:
      return True
    try: 
      # delte old tokens
      await self._password_reset_token_repo.delete_all_existing_tokens_for_user_id(session=session, user_id=user.id)
      # save new token
      random_string = secrets.token_hex(32)
      token_hash = hashlib.sha256(random_string.encode()).hexdigest()
      expiration_time = datetime.now(timezone.utc) + timedelta(seconds=180)
      await self._password_reset_token_repo.save_token_hash(session, user_id=user.id, token_hash=token_hash, expiration_time=expiration_time )
      # send email here
      print(random_string)
      return True
    except Exception as _e:
      session.rollback()
      raise HTTPException(
          status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
          detail="An error occurred while processing your password reset request."
      )
        
        
  async def reset_password(self, session: Session, token: str, new_password: str) -> bool:
    incoming_hash =  hashlib.sha256(token.encode()).hexdigest()
    hash_in_db = await self._password_reset_token_repo.get_token_object_by_hash_or_none(session=session, token_hash=incoming_hash)
    if not hash_in_db:
      raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The reset link is invalid or has already been used."
      )
    if datetime.now(timezone.utc) > hash_in_db.expires_at.astimezone(timezone.utc):
      try:
        await self._password_reset_token_repo.delete_token_by_hash(session, token_hash=incoming_hash)
      except Exception:
        session.rollback() # Clean up the database state immediately!
        
      # Still raise the intended 400 error whether the delete succeeded or failed
      raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The reset link is invalid or has already been used."
        )
    user = await self._user_service.get_user_by_id_or_none(session, user_id=hash_in_db.user_id)
    if not user:
      raise HTTPException(
          status_code=status.HTTP_404_NOT_FOUND,
          detail="User not found."
      )
    try:
        # delete token
        delete_sucess = await self._password_reset_token_repo.delete_token_by_hash(session,token_hash=incoming_hash)
        if not delete_sucess:
          raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transaction processing failure."
          ) 
        
        hashed_password = get_password_hash(new_password)
        user.hashed_password = hashed_password
        await self._user_service.update_user(session=session, user=user)
        return True
    except HTTPException:
      session.rollback()
      raise  # Re-raise explicit HTTP exceptions caught inside the block
    except Exception:
      session.rollback()
      raise HTTPException(
          status_code=status.HTTP_400_BAD_REQUEST,
          detail="Unable to reset password. Please try again."
      )
        
        
# encode token -> send token in email -> hash token -> store in db
# receive token -> hash it -> find hash in db -> if found -> remove from db, if not found -> hash is already used or is not valid 