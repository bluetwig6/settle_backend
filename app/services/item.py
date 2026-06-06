from fastapi import HTTPException, status
from sqlmodel import Session

from app.interfaces.repositories.expense import IExpenseRepository
from app.interfaces.repositories.item import IItemRepository
from app.interfaces.repositories.user import IUserRepository
from app.interfaces.services.item import IItemService
from app.models import Item, ItemCreate, User


class ItemService(IItemService):
  
  def __init__(
    self, 
    item_repo: IItemRepository,
    user_repo: IUserRepository,
    expense_repo: IExpenseRepository,
  ):
      self._item_repo = item_repo
      self._user_repo = user_repo
      self._expense_repo = expense_repo
      
  async def create_item(
    self, 
    session: Session,
    current_user: User,
    item: ItemCreate) -> Item:
    expense = await self._expense_repo.get_by_id_or_none(session=session, id=item.expense_id)
    if(not expense):
      raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail= "Expense not found with this expense id"
      )
    if(not expense.group in current_user.groups):
      credentials_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User not part of this expense's group",
        headers={"WWW-Authenticate": "Bearer"},
      )
      raise(credentials_exception)
    if(len(item.users) == 0):
      credentials_exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="No user selected",
        headers={"WWW-Authenticate": "Bearer"},
      )
      raise(credentials_exception)
    users = await self._user_repo.get_multiple_by_id(session, ids=item.users)
    if(len(users) != len(item.users)):
      raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail= "User not found for 1 or more provided user ids"
      )
    if(not all(expense.group in user.groups for user in users)):
      raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail= "One or more users not members of target expense group"
      ) 
    newItem = await self._item_repo.add(session, amount=item.amount, title=item.title, expense=expense, users=users)
    return newItem
  
  async def delete_item(self, session: Session, current_user: User, id: int) -> None:
    item = await self._item_repo.get_by_id_or_none(session, id)
    if(not item):
      raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Item not found"
      )
    if(not item.expense.group in current_user.groups):
      credentials_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User not part of this expense's group",
        headers={"WWW-Authenticate": "Bearer"},
      )
      raise credentials_exception
    return await self._item_repo.delete(session,id)