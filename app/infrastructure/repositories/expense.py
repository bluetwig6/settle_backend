from sqlmodel import Session, select

from app.interfaces.repositories.expense import IExpenseRepository
from app.models import Expense, ExpenseCreate, Group

class ExpenseRepository(IExpenseRepository):
  
  async def add(self, session: Session, group: Group, expense_data: ExpenseCreate) -> Expense:
    newExpense = Expense(title=expense_data.title)
    group.expenses.append(newExpense)
    session.add(group)
    session.commit()
    session.refresh(newExpense)
    return newExpense
  
  async def get_by_id_or_none(self, session: Session, id: int) -> Expense | None:
    expense = session.exec(select(Expense).where(Expense.id == id)).first()
    return expense