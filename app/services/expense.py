from sqlmodel import Session
from fastapi import HTTPException, status

from app.interfaces.services.expense import IExpenseService
from app.interfaces.repositories.group import IGroupRepository
from app.interfaces.repositories.expense import IExpenseRepository
from app.models import Expense, ExpenseCreate, User

class ExpenseService(IExpenseService):
  
    def __init__(self, expense_repo: IExpenseRepository, group_repo: IGroupRepository) -> None:
      self._expense_repo = expense_repo
      self._group_repo = group_repo
      
    async def add_expense(self, session: Session, current_user: User, group_id: int, expense_data: ExpenseCreate) -> Expense:
      group = await self._group_repo.get_by_id_or_none(session, id=group_id)
      
      if (not group):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail= "Group not found"
        )
    
      if(current_user in group.users):
        new_expense = await self._expense_repo.add(session,group,expense_data)
        return new_expense
      else:
        credentials_exception = HTTPException(
          status_code=status.HTTP_403_FORBIDDEN,
          detail="You cannot perform this action",
          headers={"WWW-Authenticate": "Bearer"},
        )
        raise(credentials_exception)
      
    async def get_expense(self, session: Session, current_user: User, expense_id: int) -> Expense | None:
      expense = await self._expense_repo.get_by_id_or_none(session, expense_id)
      if(not expense):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail= "Expense Not Found"
        )
      if(not expense.group in current_user.groups):
        credentials_exception = HTTPException(
          status_code=status.HTTP_403_FORBIDDEN,
          detail="User not part of this group",
          headers={"WWW-Authenticate": "Bearer"},
        )
        raise(credentials_exception)
      
      return expense