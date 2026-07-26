from typing import NotRequired
from sqlalchemy import Column
from typing_extensions import TypedDict

from sqlmodel import Field, SQLModel, Relationship, DateTime
from pydantic import BaseModel, computed_field
from datetime import datetime, timedelta, timezone


from collections import defaultdict

from pydantic import TypeAdapter

class TokenData(BaseModel):
    username: str | None = None

class ResetPasswordTokenData(BaseModel):
    email: str | None = None

class UserGroupLink(SQLModel, table=True):
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)
    group_id: int | None = Field(default=None, foreign_key="group.id", primary_key=True)

class UserItemLink(SQLModel, table=True):
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)
    item_id: int | None = Field(default=None, foreign_key="item.id", primary_key=True)

class ResetPasswordToken(BaseModel):
    reset_password_token: str
    token_type: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ResetPasswordRequestData(BaseModel):
    new_password: str
    token: str

class PasswordResetToken(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id")
    token_hash: str = Field(index=True, unique=True)
    expires_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
        default_factory=lambda: (datetime.now(timezone.utc) + timedelta(seconds=180)) # Production default fallback
    )


# CLASSES
class UserCreate(BaseModel):
    username: str = Field()
    email: str = Field()
    password: str = Field()

class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    id: int = Field(default=None, primary_key=True)

# creating table for this model as this has all the fields
class User(UserBase,table=True):
    hashed_password: str = Field()
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
        sa_type=DateTime(timezone=True)
    )
    groups: list["Group"] = Relationship(back_populates="users", link_model=UserGroupLink)
    items: list["Item"] = Relationship(back_populates="users", link_model=UserItemLink)
    payments_made: list["Payment"] = Relationship(back_populates="payer", sa_relationship_kwargs={"foreign_keys": "Payment.payer_id"})
    payments_received: list["Payment"] = Relationship(back_populates="payee", sa_relationship_kwargs={"foreign_keys": "Payment.payee_id"})
    contributions: list["Contribution"] = Relationship(back_populates="contributor", sa_relationship_kwargs={"foreign_keys": "Contribution.contributor_id"})

class UserResponse(UserBase):
    groups: list["GroupCreate"]
    
#Group
class GroupCreate(SQLModel):
    name: str = Field(index=True, unique=True)

class GroupBase(SQLModel):
    name: str = Field(index=True, unique=True)
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
        sa_type=DateTime(timezone=True)
    )

class Group(GroupBase, table=True):
    users: list[User] = Relationship(back_populates="groups", link_model=UserGroupLink)
    expenses: list["Expense"] = Relationship(back_populates="group")
    payments: list["Payment"] = Relationship(back_populates="group")

class GroupSplit(TypedDict):
    sender_id: int
    sender_username: str
    receiver_id: int
    receiver_username: str
    amount: float

class GroupResponse(GroupBase):
    users: list[UserResponse] = []
    expenses: list["ExpenseResponseWithoutGroup"] = []
    payments: list["PaymentResponse"] = []

# Expense
class ExpenseCreate(SQLModel):
    title: str

class ExpenseBase(SQLModel):
    title: str = Field(index=True)
    id: int = Field(default=None, primary_key=True)
    group_id: int = Field(default=None, foreign_key="group.id")

class Expense(ExpenseBase, table=True):
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
        sa_type=DateTime(timezone=True)
    )
    group: Group = Relationship(back_populates="expenses")
    items: list["Item"] = Relationship(back_populates="expense")
    contributions: list["Contribution"] = Relationship(back_populates="expense")

class ExpenseSplit(TypedDict):
    sender_id: int
    sender_username: str
    receiver_id: int
    receiver_username: str
    amount: float

class ExpenseSplitResponse(TypedDict):
    splits: NotRequired[list[ExpenseSplit]]
    error: NotRequired[str]

def generateExpenseSplit(items: list["ItemExposed"], contributions: list["ContributionResponse"], users: list["UserResponse"]) -> ExpenseSplitResponse:

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

class ExpenseResponseWithoutGroup(ExpenseBase):
    items: list["ItemExposed"] = []
    contributions: list["ContributionResponse"]
        
class ExpenseResponse(ExpenseBase):
    group: GroupResponse # do we need this to be this detailed ?
    items: list["ItemExposed"] = []
    contributions: list["ContributionResponse"]
    @computed_field # make this a separate route instead of a computed field
    @property
    def split(self) -> ExpenseSplitResponse:
        return generateExpenseSplit(items=self.items, contributions=self.contributions, users=self.group.users)


# Item
class ItemCreate(SQLModel):
    title: str
    amount: int = Field(default=None)
    users: list[int]
    expense_id: int

class ItemBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(nullable=False)
    amount: int = Field(default=None)
    expense_id: int = Field(default=None, foreign_key="expense.id")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
        sa_type=DateTime(timezone=True)
    )
        
class Item(ItemBase, table=True):
    users: list[User] = Relationship(back_populates="items", link_model=UserItemLink)
    expense: Expense = Relationship(back_populates="items")

class ItemExposed(ItemBase):
    users: list[UserResponse]


# Payment
class PaymentCreate(SQLModel):
    amount: int
    payer_id: int
    payee_id: int
    group_id: int

class PaymentBase(SQLModel):
    id:  int = Field(default=None, primary_key=True)
    amount: int
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
        sa_type=DateTime(timezone=True)
    )
    payer_id: int = Field(default=None, foreign_key="user.id")
    payee_id: int = Field(default=None, foreign_key="user.id")
    group_id: int = Field(default=None, foreign_key="group.id")
    
class Payment(PaymentBase, table=True):
    payer: "User" = Relationship(
        back_populates="payments_made", 
        sa_relationship_kwargs={"foreign_keys": "Payment.payer_id"}
    )
    payee: "User" = Relationship(
        back_populates="payments_received", 
        sa_relationship_kwargs={"foreign_keys": "Payment.payee_id"}
    )
    group: Group = Relationship(back_populates="payments")

class PaymentResponse(PaymentBase):
    payer: UserResponse
    payee: UserResponse
    

# Contribution

class ContributionCreate(SQLModel):
    amount: int
    contributor_id: int
    expense_id: int

class ContributionBase(SQLModel):
    id:  int = Field(default=None, primary_key=True)
    amount: int
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
        sa_type=DateTime(timezone=True)
    )
    contributor_id: int = Field(default=None, foreign_key="user.id")
    expense_id: int = Field(default=None, foreign_key="expense.id")
    
class Contribution(ContributionBase, table=True):
    contributor: "User" = Relationship(
        back_populates="contributions", 
        sa_relationship_kwargs={"foreign_keys": "Contribution.contributor_id"}
    )
    expense: Expense = Relationship(back_populates="contributions")

class ContributionResponse(ContributionBase):
    contributor: UserResponse
    
    
# response models


class GroupDetail(SQLModel):
    id: int
    name: str
    member_count: int
    expense_count: int
    