from fastapi import APIRouter, Response

from app.core.dependecies import DCurrentUser, DPaymentService, SessionDep
from app.models import PaymentCreate, PaymentResponse


router = APIRouter()

@router.post("/", response_model=PaymentResponse)
async def add_payment(
  session: SessionDep,
  payment_service: DPaymentService,
  payment_create: PaymentCreate,
  current_user: DCurrentUser
):
  payment = await payment_service.create_payment(session,current_user,payment_create)
  return payment

@router.delete("/", response_model=None)
async def delete_item(
  session: SessionDep,
  payment_service: DPaymentService,
  current_user: DCurrentUser,
  id: int
):
  await payment_service.delete_payment(session,current_user,id)
  return Response(status_code=204)