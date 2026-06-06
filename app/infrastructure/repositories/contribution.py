from sqlmodel import Session, select

from app.interfaces.repositories.contribution import IContributionRepository
from app.models import Contribution, ContributionResponse, Expense, User

class ContributionRepository(IContributionRepository):

  async def add(self, session: Session, amount: int, expense: Expense, contributor: User) -> ContributionResponse:
    new_contribution = Contribution(amount=amount,expense=expense, contributor=contributor)
    session.add(new_contribution)
    session.commit()
    return ContributionResponse.model_validate(new_contribution)    
  
  async def delete(self, session: Session, id: int) -> None:
    contribution = session.exec(select(Contribution).where(Contribution.id == id)).first()
    session.delete(contribution)
    session.commit()
    return None
  
  async def get_by_id_or_none(self, session: Session, id: int) -> ContributionResponse | None:
    contribution = session.exec(select(Contribution).where(Contribution.id == id)).first()
    return ContributionResponse.model_validate(contribution)    
    