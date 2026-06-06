import abc
from sqlmodel import Session
from app.models import ExpenseCreate, Expense, User

class IExpenseService(abc.ABC):
  
  @abc.abstractmethod
  async def add_expense(self, session: Session, current_user:User, group_id: int, expense_data:ExpenseCreate ) -> Expense:...
  
  @abc.abstractmethod
  async def get_expense(self, session:Session, current_user:User, expense_id:int) -> Expense|None: ...
  