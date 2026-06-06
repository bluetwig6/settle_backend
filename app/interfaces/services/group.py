import abc
from app.models import Group, GroupDetail, GroupSplit, User, GroupCreate
from sqlmodel import Session

class IGroupService(abc.ABC):
  
  @abc.abstractmethod
  async def create_group(self,session:Session, current_user: User, group_data: GroupCreate) -> Group: ...
  
  @abc.abstractmethod
  async def get_by_id_or_none(self, session:Session, group_id: int) -> Group | None: ...

  @abc.abstractmethod
  async def get_split(self, session:Session, current_user: User, group_id: int) -> list[GroupSplit]: ...
  
  @abc.abstractmethod
  async def get_group_detail_by_id(self, session:Session, id: int) -> GroupDetail | None: ...
  