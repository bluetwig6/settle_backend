from fastapi import  APIRouter
from sqlmodel import select
from sqlmodel import select
from app.models import User, UserBase, UserResponse
from app.core.dependecies import SessionDep, DCurrentUser, DUserService
router = APIRouter()

@router.get("/")
async def read_users_me(
    current_user: DCurrentUser,
) -> UserBase:
    return current_user


@router.get("/all", response_model=list[UserBase])
async def get_users(session: SessionDep):
    users = session.exec(select(User)).all()
    return users

@router.get("/{search_query}", response_model=list[UserResponse])
async def search_users(
    search_query: str,
    session: SessionDep,
    current_user: DCurrentUser,
    user_service: DUserService
):
    users = await user_service.search_users(session, search_query)
    return users

