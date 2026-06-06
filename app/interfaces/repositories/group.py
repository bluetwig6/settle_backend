import abc
from sqlmodel import Session
from app.models import Group, GroupCreate, GroupDetail, User

class IGroupRepository(abc.ABC):
  
  @abc.abstractmethod
  async def create(self, session: Session, user: User, group_data: GroupCreate) -> Group: ...
  
  @abc.abstractmethod
  async def get_by_id_or_none(self, session: Session, id: int) -> Group | None: ...

  @abc.abstractmethod
  async def get_detail_by_id(self, session: Session, id: int) -> GroupDetail | None: ...