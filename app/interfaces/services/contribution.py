import abc

from sqlmodel import Session

from app.models import ContributionCreate, ContributionResponse, User

class IContributionService(abc.ABC):
  
  @abc.abstractmethod
  async def create_contribution(self, session: Session, current_user: User, contribution_create: ContributionCreate ) -> ContributionResponse: ...
  
  @abc.abstractmethod
  async def delete_contribution(self, session: Session, current_user: User, id: int) -> None: ...
  