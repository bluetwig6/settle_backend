from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.models import Token, UserBase, UserCreate
from app.core.dependecies import SessionDep, DUserAuthService
from app.config import get_app_settings

from fastapi import APIRouter

router = APIRouter()

settings = get_app_settings()

@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
    user_auth_service: DUserAuthService
) -> Token:
    return await user_auth_service.sign_in_user(session, form_data)

@router.post("/sign-up", response_model=UserBase)
async def sign_up(user: UserCreate, session: SessionDep, user_auth_service: DUserAuthService):
    return await user_auth_service.sign_up_user(session, user)