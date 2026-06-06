from fastapi import APIRouter

from app.core.dependecies import DCurrentUser, DExpenseervice, SessionDep
from app.models import  ExpenseResponse


router = APIRouter()

@router.get("/{id}", response_model=ExpenseResponse)
async def get_expense(
  session: SessionDep,
  current_user: DCurrentUser,
  id: int,
  expense_service: DExpenseervice
):
  expense = await expense_service.get_expense(session, current_user, id)
  print("expense: ", expense)
  return expense