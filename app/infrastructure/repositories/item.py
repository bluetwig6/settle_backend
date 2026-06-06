from sqlmodel import Session, select

from app.interfaces.repositories.item import IItemRepository
from app.models import Expense, User, Item

class ItemRepository(IItemRepository):
  
  async def add(self, session: Session, amount: int, title: str, expense: Expense, users: list[User]) -> Item:
    new_item = Item(amount=amount, title=title, expense=expense, users=users)
    session.add(new_item)
    session.commit()
    return new_item
  
  async def delete(self, session: Session, id: int) -> None:
    item = session.exec(select(Item).where(Item.id == id)).first()
    session.delete(item)
    session.commit()
    return None
  
  async def get_by_id_or_none(self, session: Session, id: int) -> Item | None:
    item = session.exec(select(Item).where(Item.id == id)).first()
    return item
    