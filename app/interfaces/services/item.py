import abc

from sqlmodel import Session

from app.models import Item, ItemCreate, User

class IItemService(abc.ABC):
  
  @abc.abstractmethod
  async def create_item(self, session: Session,current_user: User, item: ItemCreate) -> Item: ...
  
  @abc.abstractmethod
  async def delete_item(self, session: Session,current_user: User, id: int) -> None: ...