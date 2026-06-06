from sqlmodel import Session, select

from app.interfaces.repositories.payment import IPaymentRepository
from app.models import Group, Payment, PaymentResponse, User

class PaymentRepository(IPaymentRepository):
  
  async def add(self, session: Session, amount: int, group: Group, payer: User, payee: User) -> PaymentResponse:
    new_payment = Payment(amount=amount,group=group, payer=payer,payee=payee)
    session.add(new_payment)
    session.commit()
    return PaymentResponse.model_validate(new_payment) 
    
  async def delete(self, session: Session, id: int) -> None:
    payment = session.exec(select(Payment).where(Payment.id == id)).first()
    session.delete(payment)
    session.commit()
    return None
  
  async def get_by_id_or_none(self, session: Session, id: int) -> PaymentResponse | None:
    payment = session.exec(select(Payment).where(Payment.id == id)).first()
    return PaymentResponse.model_validate(payment)
    