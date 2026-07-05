from typing import Annotated

from sqlmodel import Session, create_engine, select
from pwdlib import PasswordHash
from app.models import User, UserGroupLink, Group, Expense
from fastapi import Depends, HTTPException, Path, status
from fastapi.security import OAuth2PasswordBearer
from app.models import TokenData, Item
from app.config import get_app_settings

from app.services import user
from app.services.contribution import ContributionService
from app.services.item import ItemService
from app.services.payment import PaymentService
from app.services.user import UserService
from app.services.auth import UserAuthService
from app.services.auth_token import AuthTokenService
from app.services.group import GroupService
from app.services.expense import ExpenseService

from app.core.providers import get_contribution_service, get_item_service, get_payment_service, get_user_service
from app.core.providers import get_user_auth_service
from app.core.providers import get_auth_token_service
from app.core.providers import get_group_service
from app.core.providers import get_expense_service

password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash("dummypassword")


settings = get_app_settings()
SECRET_KEY = settings.jwt_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt_access_token_expire_minutes
ALGORITHM = settings.jwt_algorithm
engine_props = settings.sqlalchemy_engine_props
engine = create_engine(engine_props["url"], echo=engine_props["echo"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/token")


def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
JWT_TOKEN = Annotated[str, Depends(oauth2_scheme)]


DUserService = Annotated[UserService, Depends(get_user_service)]
DUserAuthService = Annotated[UserAuthService, Depends(get_user_auth_service)]
DAuthTokenService = Annotated[AuthTokenService, Depends(get_auth_token_service)]
DGroupService = Annotated[GroupService, Depends(get_group_service)]
DExpenseervice = Annotated[ExpenseService, Depends(get_expense_service)]
DItemService = Annotated[ItemService, Depends(get_item_service)]
DPaymentService = Annotated[PaymentService, Depends(get_payment_service)]
DContributionService = Annotated[ContributionService, Depends(get_contribution_service)]

async def get_current_user(
    token: JWT_TOKEN, 
    session: SessionDep,
    auth_token_service: DAuthTokenService,
    user_service: DUserService
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = await auth_token_service.parse_jwt_token(token)
    username = payload.get("sub")
    token_data = TokenData(username=username)
    if not token_data.username:
        raise credentials_exception
    user = await user_service.get_user_by_username(session=session, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


# async def user_in_expense_group(
#     session: SessionDep,
#     user_service: 
# ):
    

DCurrentUser = Annotated[User, Depends(get_current_user)]


async def is_current_user_in_Group(
    current_user: DCurrentUser,
    group_id: Annotated[int, Path(title="The ID of the group to get")],
    session: SessionDep
):
    statement = (
        select(
            UserGroupLink.group_id
        )
        .where(UserGroupLink.user_id == current_user.id)    
    )
    
    user_group_ids = session.exec(statement).all()
    
    if not group_id in user_group_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not part of targeted group",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return current_user

async def is_current_user_in_item_group(
    current_user: DCurrentUser,
    item_id: Annotated[int, Path(title="The ID of the item")],
    session: SessionDep
):
    
    group_id_statement = (
        select(Group.id)
        .outerjoin(Expense, Group.id == Expense.group_id)
        .outerjoin(Item, Expense.id == Item.expense_id)
        .where(Item.id == item_id)    
    )
    
    user_group_id_statement = (
        select(
            UserGroupLink.group_id
        )
        .where(UserGroupLink.user_id == current_user.id)    
    )
    
    user_group_ids = session.exec(user_group_id_statement).all()
    item_group_id = session.exec(group_id_statement).first()
    print( user_group_ids, item_group_id)
    if not item_group_id in user_group_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not part of this item's group",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return current_user
        
DCurrentUserInGroup = Annotated[User, Depends(is_current_user_in_Group)]
DCurrentUserInItemGroup = Annotated[User, Depends(is_current_user_in_item_group)]