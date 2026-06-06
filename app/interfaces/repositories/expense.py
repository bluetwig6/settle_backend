import abc
from sqlmodel import Session
from app.models import ExpenseCreate, Expense, Group

class IExpenseRepository(abc.ABC):
  
  @abc.abstractmethod
  async def add(self, session: Session, group: Group, expense_data: ExpenseCreate) -> Expense: ...

  @abc.abstractmethod
  async def get_by_id_or_none(self, session: Session, id: int) -> Expense|None: ...