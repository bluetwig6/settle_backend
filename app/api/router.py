from fastapi import APIRouter
from app.api.routes import authentication, contribution, groups, users, item, expense, payment

router = APIRouter()

router.include_router(router=groups.router, tags=['Group'], prefix='/groups')
router.include_router(router=authentication.router, tags=['Authentication'], prefix='/users')
router.include_router(router=users.router, tags=['User'], prefix='/user')
router.include_router(router=item.router, tags=['Item'], prefix='/item')
router.include_router(router=expense.router, tags=['Expense'], prefix='/expense')
router.include_router(router=payment.router, tags=['Payment'], prefix='/payment')
router.include_router(router=contribution.router, tags=['Contribution'], prefix='/contribution')