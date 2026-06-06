from typing import Annotated

from fastapi import HTTPException, status, Path, APIRouter
from sqlmodel import select
from app.models import GroupDetail, GroupResponse, GroupCreate, Group, ExpenseCreate, Expense, GroupSplit
from app.core.dependecies import DCurrentUserInGroup, SessionDep, DCurrentUser, DUserService, DGroupService, DExpenseervice

router = APIRouter()

@router.post("/", response_model=GroupResponse)
async def create_group(
    current_user: DCurrentUser,
    group_data: GroupCreate, 
    session: SessionDep,
    group_service: DGroupService
):
    new_group = await group_service.create_group(session,current_user,group_data )
    return new_group


@router.get("/", response_model=list[GroupResponse])
async def groups(
    current_user: DCurrentUser,
    session: SessionDep
):
    return current_user.groups

@router.get("/detail/{group_id}", response_model=GroupDetail | None)
async def get_group_detail(
    group_id: Annotated[int, Path(title="The ID of the group to get")],
    session: SessionDep,
    current_user: DCurrentUserInGroup,
    group_service: DGroupService
) -> GroupDetail:
    
    result = await group_service.get_group_detail_by_id(session=session, id=group_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail= "Group not found"
        )
    
    return GroupDetail.model_validate(result)
    
    # group name, member count, expense count, 

@router.get("/{group_id}", response_model=GroupResponse)
async def group(
    group_id: Annotated[str, Path(title="The ID of the group to get")],
    session: SessionDep,
    current_user: DCurrentUser,
    group_service: DGroupService
):

    group = await group_service.get_by_id_or_none(session, int(group_id))
    if not group:
         raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail= "Group not found"
        )
    if(current_user in group.users):
        return group
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You cannot perform this action",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/split/{group_id}", response_model=list[GroupSplit])
async def get_group_splti(
    group_id: Annotated[str, Path(title="The ID of the group to get")],
    session: SessionDep,
    current_user: DCurrentUser,
    group_service: DGroupService
):

    split = await group_service.get_split(session, current_user=current_user, group_id=int(group_id))
    return split



@router.put("/remove-user/{group_id}/{user_id}", response_model=GroupResponse)
async def removeUserFromGroup(
    group_id: Annotated[int, Path(title="The ID of the group to update")],
    user_id: Annotated[int, Path(title="The ID of the user to remove")],
    session: SessionDep,
    current_user: DCurrentUser,
    user_service: DUserService
):
    await user_service.remove_user_from_group(session, current_user, group_id, user_id)
    newGroup = session.exec(select(Group).where(Group.id == group_id)).one()
    return newGroup

@router.put("/add-user/{group_id}/{user_id}", response_model=GroupResponse)
async def addUserToGroup(
    group_id: Annotated[int, Path(title="The ID of the group to update")],
    user_id: Annotated[int, Path(title="The ID of the user to remove")],
    session: SessionDep,
    current_user: DCurrentUser,
    user_service: DUserService
):
    await user_service.add_user_to_group(session, current_user, group_id, user_id)
    updated_group = session.exec(select(Group).where(Group.id == group_id)).one()
    return updated_group


# check for migrations and throwing errors
@router.post("/{group_id}/expense", response_model=Expense)
async def addExpense(
    group_id: Annotated[int, Path(title="The ID of the group to update")],
    expense_data: ExpenseCreate,
    session: SessionDep,
    current_user: DCurrentUser,
    expense_service: DExpenseervice
):
    new_expense = await expense_service.add_expense(session, current_user, group_id, expense_data)
    return new_expense
