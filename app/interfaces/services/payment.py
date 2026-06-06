import abc

from sqlmodel import Session

from app.models import PaymentCreate, PaymentResponse, User

class IPaymentService(abc.ABC):
  
  @abc.abstractmethod
  async def create_payment(self, session: Session,current_user: User, payment_create: PaymentCreate ) -> PaymentResponse: ...
  
  @abc.abstractmethod
  async def delete_payment(self, session: Session,current_user: User, id: int) -> None: ...
  