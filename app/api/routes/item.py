from fastapi import APIRouter, Response

from app.core.dependecies import DCurrentUser, DItemService, SessionDep
from app.models import ItemCreate, ItemExposed


router = APIRouter()

@router.post("/", response_model=ItemExposed)
async def add_item(
  session: SessionDep,
  item_service: DItemService,
  item_data: ItemCreate,
  current_user: DCurrentUser
):
  item = await item_service.create_item(session,current_user,item=item_data)
  return item

@router.delete("/", response_model=None)
async def delete_item(
  session: SessionDep,
  item_service: DItemService,
  current_user: DCurrentUser,
  id: int
):
  await item_service.delete_item(session,current_user,id )
  return Response(status_code=204)