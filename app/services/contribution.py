

from fastapi import HTTPException,status
from sqlmodel import Session

from app.core.validations import expense_exists, group_exists, raise_error_if_current_user_not_in_group, user_exists
from app.interfaces.repositories.contribution import IContributionRepository
from app.interfaces.repositories.expense import IExpenseRepository
from app.interfaces.repositories.group import IGroupRepository
from app.interfaces.repositories.user import IUserRepository
from app.interfaces.services.contribution import IContributionService
from app.models import ContributionCreate, ContributionResponse, User


class ContributionService(IContributionService):
  
  def __init__(
    self,
    user_repo: IUserRepository,
    group_repo: IGroupRepository,
    expense_repo: IExpenseRepository,
    contribution_repo: IContributionRepository
  ):
    self._user_repo = user_repo
    self._group_repo = group_repo
    self._expense_repo= expense_repo
    self._contribution_repo= contribution_repo
    
  async def create_contribution(self, session: Session, current_user: User, contribution_create: ContributionCreate) -> ContributionResponse:
    contributor_user = await self._user_repo.get_by_id(session=session, id=contribution_create.contributor_id)
    expense = await self._expense_repo.get_by_id_or_none(session,id=contribution_create.expense_id)
    
    safe_contributor_user = user_exists(contributor_user)
    safe_expense = expense_exists(expense)
  
    group = safe_expense.group
    safe_group = group_exists(group)
    
    raise_error_if_current_user_not_in_group(user=current_user, group=safe_group)
    raise_error_if_current_user_not_in_group(user=safe_contributor_user, group=safe_group)
    
    contribution = await self._contribution_repo.add(session,amount=contribution_create.amount, expense=safe_expense, contributor=safe_contributor_user)
    return contribution
  
  async def delete_contribution(self, session: Session, current_user: User, id: int) -> None:
    contribution = await self._contribution_repo.get_by_id_or_none(session, id)
    if not contribution:
      raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Contribution not found"
      )
  
    group = await self._group_repo.get_by_id_or_none(session, contribution.expense.group_id)
    safe_group = group_exists(group)
    
    raise_error_if_current_user_not_in_group(user=current_user, group=safe_group)

    await self._contribution_repo.delete(session, id=contribution.id)