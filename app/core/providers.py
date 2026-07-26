from app.infrastructure.repositories.contribution import ContributionRepository
from app.infrastructure.repositories.item import ItemRepository
from app.infrastructure.repositories.passwordResetToken import PasswordResetTokenRespository
from app.infrastructure.repositories.payment import PaymentRepository
from app.interfaces.repositories.contribution import IContributionRepository
from app.interfaces.repositories.item import IItemRepository
from app.interfaces.repositories.passwordResetToken import IPasswordResetTokenRepository
from app.interfaces.repositories.payment import IPaymentRepository
from app.interfaces.repositories.user import IUserRepository
from app.interfaces.repositories.group import IGroupRepository 
from app.interfaces.repositories.expense import IExpenseRepository
from app.interfaces.services.contribution import IContributionService
from app.interfaces.services.item import IItemService
from app.interfaces.services.payment import IPaymentService
from app.interfaces.services.user import IUserService
from app.interfaces.services.auth import IUserAuthService
from app.interfaces.services.auth_token import IAuthTokenService
from app.interfaces.services.group import IGroupService
from app.interfaces.services.expense import IExpenseService 

from app.infrastructure.repositories.user import UserRepository
from app.infrastructure.repositories.group import GroupRepository
from app.infrastructure.repositories.expense import ExpenseRepository

from app.services.contribution import ContributionService
from app.services.item import ItemService
from app.services.payment import PaymentService
from app.services.user import UserService
from app.services.auth import UserAuthService
from app.services.auth_token import AuthTokenService
from app.services.group import GroupService
from app.services.expense import ExpenseService

from app.config import get_app_settings

# REPOSITORIES
def get_user_repo() -> IUserRepository:
  return UserRepository()

def get_group_repo() -> IGroupRepository:
  return GroupRepository()

def get_expense_repo() -> IExpenseRepository:
  return ExpenseRepository()

def get_item_repo() -> IItemRepository:
  return ItemRepository()

def get_payment_repo() -> IPaymentRepository:
  return PaymentRepository()

def get_contribution_repo() -> IContributionRepository:
  return ContributionRepository()

def get_password_reset_token_repo() -> IPasswordResetTokenRepository:
  return PasswordResetTokenRespository()

# SERVICES
def get_user_service() -> IUserService:
  return UserService(user_repo=get_user_repo(), group_repo=get_group_repo())

def get_auth_token_service() -> IAuthTokenService:
  settings = get_app_settings()
  return AuthTokenService(
      secret_key=settings.jwt_secret_key,
      token_expiration_minutes=settings.jwt_access_token_expire_minutes,
      algorithm=settings.jwt_algorithm,
  )

def get_user_auth_service() -> IUserAuthService:
  return UserAuthService(user_service=get_user_service(), auth_token_service=get_auth_token_service(), password_reset_token_repo=get_password_reset_token_repo())

def get_group_service() -> IGroupService:
  return GroupService(group_repo=get_group_repo())

def get_expense_service() -> IExpenseService:
  return ExpenseService(expense_repo=get_expense_repo(), group_repo=get_group_repo())

def get_item_service() -> IItemService:
  return ItemService(item_repo=get_item_repo(), user_repo=get_user_repo(), expense_repo=get_expense_repo())

def get_payment_service() -> IPaymentService:
  return PaymentService(user_repo=get_user_repo(), group_repo=get_group_repo(), payment_repo=get_payment_repo())

def get_contribution_service() -> IContributionService:
  return ContributionService(user_repo=get_user_repo(), group_repo=get_group_repo(), expense_repo=get_expense_repo(), contribution_repo=get_contribution_repo())