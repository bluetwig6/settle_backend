from typing import Annotated
from fastapi import Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from app.models import ResetPasswordRequestData, Token, UserBase, UserCreate
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

@router.post("/forgot-password")
async def forgot_password(email: str, session: SessionDep, authService: DUserAuthService) -> JSONResponse:
    _ = await authService.send_reset_password_email(session, email)
    return JSONResponse(status_code=status.HTTP_200_OK,
           content={"message": "Email has been sent", "success": True})
    
@router.put("/reset-password")
async def reset_password(
    session: SessionDep, 
    password_data: ResetPasswordRequestData,
    authService: DUserAuthService) -> JSONResponse:
    success = await authService.reset_password(session=session, token=password_data.token, new_password=password_data.new_password)
    if success:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Password Reset Successfully", "success": True})
    else:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": "Unable to reset password", "success": True})