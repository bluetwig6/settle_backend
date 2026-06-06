from sqlmodel import Session, col

from app.interfaces.repositories.group import IGroupRepository
from app.models import Expense, GroupCreate, GroupDetail, User, Group, UserGroupLink
from sqlmodel import select, func, col

class GroupRepository(IGroupRepository):
  
  async def create(self, session: Session, user: User, group_data: GroupCreate) -> Group:
    newGroup = Group(name=group_data.name)
    user.groups.append(newGroup)
    session.add(newGroup)
    session.commit()
    session.refresh(newGroup)
    session.refresh(user)
    return newGroup
  
  async def get_by_id_or_none(self, session: Session, id: int) -> Group | None:
    group = session.exec(select(Group).where(Group.id == int(id))).first()
    return group
  
  async def get_detail_by_id(self, session: Session, id: int) -> GroupDetail | None:
    group_id= id
    statement = (
        select(
            Group.id,
            Group.name,
            func.count(col(Expense.id).distinct()).label("expense_count"),
            func.count(col(UserGroupLink.user_id).distinct()).label("member_count")
        )
        .outerjoin(Expense, col(Expense.group_id) == Group.id )
        .outerjoin(UserGroupLink, col(UserGroupLink.group_id) == Group.id)
        .where(Group.id == group_id)
        .group_by(col(Group.id))
        
    )
    
    result = session.exec(statement).first()
    if not result:
      return None
    
    return GroupDetail.model_validate(result)

          