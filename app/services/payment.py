from fastapi import HTTPException, status
from sqlmodel import Session

from app.core.validations import group_exists, raise_error_if_current_user_not_in_group, raise_error_if_not_in_group, user_exists
from app.interfaces.repositories.group import IGroupRepository
from app.interfaces.repositories.payment import IPaymentRepository
from app.interfaces.repositories.user import IUserRepository
from app.interfaces.services.payment import IPaymentService
from app.models import  PaymentCreate, PaymentResponse, User

class PaymentService(IPaymentService):
  
  def __init__(
    self, 
    user_repo: IUserRepository,
    group_repo: IGroupRepository,
    payment_repo: IPaymentRepository
  ):
    self._user_repo = user_repo
    self._group_repo = group_repo
    self._payment_repo = payment_repo
    
  async def create_payment(self, session: Session, current_user: User, payment_create: PaymentCreate) -> PaymentResponse:
    payer_user = await self._user_repo.get_by_id(session=session, id=payment_create.payer_id)
    payee_user = await self._user_repo.get_by_id(session=session, id=payment_create.payee_id)
    group = await self._group_repo.get_by_id_or_none(session=session, id=payment_create.group_id)
    
    safe_payer_user = user_exists(payer_user)
    safe_payee_user = user_exists(payee_user)
    safe_group = group_exists(group)    
    raise_error_if_current_user_not_in_group(user=current_user, group=safe_group)
    raise_error_if_not_in_group(users=[safe_payee_user, safe_payer_user], group=safe_group)
    
    payment = await self._payment_repo.add(
      session=session,
      amount=payment_create.amount,
      group=safe_group,
      payer=safe_payer_user,
      payee=safe_payee_user)
    return payment
  
  async def delete_payment(self, session: Session, current_user: User, id: int) -> None:
    payment = await self._payment_repo.get_by_id_or_none(session, id)
    if not payment:
      raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Payment not found"
      )
    group = await self._group_repo.get_by_id_or_none(session, payment.group_id)
    safe_group =group_exists(group)
    raise_error_if_current_user_not_in_group(user=current_user, group=safe_group)
    
    await self._payment_repo.delete(session, id=payment.id)
    
    