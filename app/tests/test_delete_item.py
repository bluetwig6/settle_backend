
from typing import Any

from fastapi.testclient import TestClient

from app.core.dependecies import get_current_user
from app.main import app 
from app.tests.factories.group import GroupFactory
from app.tests.factories.user import UserFactory
from app.tests.factories.expense import ExpenseFactory
from app.tests.factories.item import ItemFactory


def test_delete_item_in_users_group(auth_client: TestClient):
  userCurrent = UserFactory()
  group = GroupFactory()
  expense = ExpenseFactory(group_id=group.id)
  item = ItemFactory(expense_id=expense.id)
  
  def return_user() -> dict[str,Any]:
    return userCurrent
  
  group.users.append(userCurrent)
  
  app.dependency_overrides[get_current_user] = return_user
  
  response = auth_client.delete(f"/api/item/{item.id}")
  assert response.status_code == 204
  assert response.text == ""
  
  
def test_delete_item_not_in_users_group(auth_client: TestClient):
  userCurrent = UserFactory()
  userInGroup = UserFactory()
  group = GroupFactory()
  expense = ExpenseFactory(group_id=group.id)
  item = ItemFactory(expense_id=expense.id)
  
  def return_user() -> dict[str,Any]:
    return userCurrent
  
  group.users.append(userInGroup)
  
  app.dependency_overrides[get_current_user] = return_user
  
  response = auth_client.delete(f"/api/item/{item.id}")
  assert response.status_code == 403
  assert response.json()["detail"] == "User not part of this item's group"
  
  
def test_non_existent_item(auth_client: TestClient):
  userCurrent = UserFactory()
  
  def return_user() -> dict[str,Any]:
    return userCurrent
    
  app.dependency_overrides[get_current_user] = return_user
  
  response = auth_client.delete(f"/api/item/1")
  assert response.status_code == 403
  assert response.json()["detail"] == "User not part of this item's group"
  