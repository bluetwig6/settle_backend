from fastapi import APIRouter, Response

from app.core.dependecies import DContributionService, DCurrentUser, SessionDep
from app.models import ContributionCreate, ContributionResponse


router = APIRouter()

@router.post("/", response_model=ContributionResponse)
async def add_contribution(
  session: SessionDep,
  contribution_service: DContributionService,
  contribution_create: ContributionCreate,
  current_user: DCurrentUser
):
  contribution = await contribution_service.create_contribution(session,current_user,contribution_create)
  return contribution

@router.delete("/", response_model=None)
async def delete_item(
  session: SessionDep,
  contribution_service: DContributionService,
  current_user: DCurrentUser,
  id: int
):
  await contribution_service.delete_contribution(session,current_user,id)
  return Response(status_code=204)