from fastapi import APIRouter, Response, Path
from typing import Annotated
from app.core.dependecies import DCurrentUser, DItemService, SessionDep, DCurrentUserInItemGroup
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

@router.delete("/{item_id}", response_model=None)
async def delete_item(
  session: SessionDep,
  item_service: DItemService,
  current_user: DCurrentUserInItemGroup,
  item_id: Annotated[int, Path(title="The ID of the item to be deleted")]
):
  await item_service.delete_item(session,current_user,id=item_id )
  return Response(status_code=204)