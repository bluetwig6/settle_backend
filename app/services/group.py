from collections import defaultdict
from fastapi import HTTPException, status
from pydantic import TypeAdapter
from sqlmodel import Session

from app.interfaces.services.group import IGroupService
from app.interfaces.repositories.group import IGroupRepository
from app.models import Contribution, ExpenseSplit, ExpenseSplitResponse, Group, GroupDetail, GroupSplit, Item, Payment,User, GroupCreate

def generateExpenseSplit(items: list[Item], contributions: list[Contribution], users: list[User]) -> ExpenseSplitResponse:

    total_cost = sum(item.amount for item in items)
    total_contributions = sum(contribution.amount for contribution in contributions)
    user_dict = {user.id: user.username for user in users}
    if(total_cost != total_contributions):
      return {
        "error" : "Unable to calculate split. Total contributions don't equal total item amount."
      }
  
    contributions_map:dict[int,float] = defaultdict(float)
    for contribution in contributions:
      contributions_map[contribution.contributor_id] += contribution.amount
      
    consumptions_map:dict[int,float] = defaultdict(float)
    for item in items:
        amount_per_user = item.amount/len(item.users)
        for user in item.users:
            consumptions_map[user.id] += amount_per_user

    balances:dict[int,float] = defaultdict(float)
    for user in users:
      balances[user.id] = (contributions_map[user.id] - consumptions_map[user.id])
    
    receivers= sorted([[user, balance] for user, balance in balances.items() if balance > 0], key=lambda entry: entry[1],reverse=True)
    senders= sorted([[user, abs(balance)] for user, balance in balances.items() if balance < 0], key=lambda entry: entry[1],reverse=True)
    transactions: list[dict[str,float|int|str]] = []
    
    receiver_idx, sender_idx = 0,0
    while receiver_idx < len(receivers) and sender_idx < len(senders):
      receiver_id, receiver_gets = receivers[receiver_idx]
      sender_id, sender_sends = senders[sender_idx]
    
    
      settle_amount = min(receiver_gets, sender_sends)
      
      transactions.append({
        "sender_id": sender_id,
        "sender_username": user_dict[int(sender_id)],
        "receiver_id": receiver_id,
        "receiver_username": user_dict[int(receiver_id)],
        "amount": settle_amount
      })
      
      receivers[receiver_idx][1] -= settle_amount
      senders[sender_idx][1] -= settle_amount
      
      if receivers[receiver_idx][1] <= 0:
        receiver_idx +=1 
      else:
        sender_idx +=1 

    adapter = TypeAdapter(list[ExpenseSplit])

    return {
      "splits" :adapter.validate_python(transactions),
      }

def generateGroupSplit(expenseSplits:list[ExpenseSplit], payments: list[Payment],users: list[User]) -> list[GroupSplit]:
    aggregated_splits:dict[tuple[int,int],float] = {}
    formatted_split:list[GroupSplit] = []
    user_dict = {user.id: user.username for user in users}
    
    for expenseSplit in expenseSplits:
        if (expenseSplit["sender_id"],expenseSplit["receiver_id"]) in aggregated_splits:
            aggregated_splits[(expenseSplit["sender_id"],expenseSplit["receiver_id"])] += expenseSplit["amount"]
        elif (expenseSplit["receiver_id"],expenseSplit["sender_id"]) in aggregated_splits:
            aggregated_splits[(expenseSplit["receiver_id"],expenseSplit["sender_id"])] -= expenseSplit["amount"]
        else:
            aggregated_splits[(expenseSplit["sender_id"],expenseSplit["receiver_id"])] = expenseSplit["amount"]

    for payment in payments:
        if (payment.payer_id,payment.payee_id) in aggregated_splits:
            aggregated_splits[(payment.payer_id,payment.payee_id)] -= payment.amount
        elif (payment.payee_id,payment.payer_id) in aggregated_splits:
            aggregated_splits[(payment.payee_id,payment.payer_id)] += payment.amount
        else:
            aggregated_splits[(payment.payer_id,payment.payee_id)] = -1*payment.amount
    for key,value in aggregated_splits.items():
        if(aggregated_splits[key] < 0):
            formatted_split.append({
                "sender_id": key[1],
                "sender_username": user_dict[key[1]],
                "receiver_id": key[0],
                "receiver_username": user_dict[key[0]],
                "amount": -1* value
            })
        else:
            formatted_split.append({
                "sender_id": key[0],
                "sender_username": user_dict[key[0]],
                "receiver_id": key[1],
                "receiver_username":user_dict[key[1]],
                "amount": value
            })
    return formatted_split


class GroupService(IGroupService):
  def __init__(
    self, 
    group_repo: IGroupRepository
  ):
      self._group_repo = group_repo

  async def get_by_id_or_none(self, session: Session, group_id: int) -> Group | None:
    group = await self._group_repo.get_by_id_or_none(session, id=group_id)
    return group

  async def create_group(self, session: Session, current_user: User, group_data: GroupCreate) -> Group:
    group = await self._group_repo.create(session, user=current_user, group_data=group_data)
    return group 
  
  async def get_split(self, session: Session,current_user: User, group_id: int) -> list[GroupSplit]:
    group = await self._group_repo.get_by_id_or_none(session, group_id)
    if not group:
      credentials_exception = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Group not found",
      )
      raise(credentials_exception)
    
    if not current_user in group.users:
      credentials_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User not part of this group",
      )
      raise(credentials_exception)
    
    expenses = group.expenses
    expenseSplits:list[ExpenseSplit] = []
    for expense in expenses:
      split = generateExpenseSplit(items= expense.items, contributions = expense.contributions, users= group.users)
      if "splits" in split:
          expenseSplits += split["splits"]
    
    return(generateGroupSplit(expenseSplits=expenseSplits,payments=group.payments, users=group.users))
    

  async def get_group_detail_by_id(self, session: Session, id: int) -> GroupDetail | None:
    detail = await self._group_repo.get_detail_by_id(session,id)
    return detail
    