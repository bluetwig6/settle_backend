from fastapi import HTTPException, status

from app.models import Expense, Group, User


def user_exists(user: User | None) -> User:
  if user:
    return user 
  raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User not found with this id"
  )
  
def expense_exists(expense: Expense | None) -> Expense:
  if expense:
    return expense 
  raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Expense not found with this id"
  )
  
def group_exists(group: Group | None) -> Group:
  if group:
    return group 
  raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Group not found with this id"
  )

def raise_error_if_not_in_group(users: list[User], group: Group):
  if(not all(user in group.users for user in users)):
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail= "Users not in group"
    )
    
def raise_error_if_current_user_not_in_group(user: User, group: Group):
  if(not user in group.users):
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      detail= "User not allowed this action"
    )
