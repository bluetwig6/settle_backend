
from typing import Any

from fastapi.testclient import TestClient

from app.core.dependecies import get_current_user
from app.main import app 
from app.tests.factories.group import GroupFactory
from app.tests.factories.user import UserFactory


def test_create_payment_with_current_user_in_group(auth_client: TestClient):
  userCurrent = UserFactory()
  group = GroupFactory()
  userPayer = UserFactory()
  userPayee = UserFactory()
  group.users.append(userCurrent)
  group.users.append(userPayee)
  group.users.append(userPayer)

  def return_user() -> dict[str,Any]:
    return userCurrent


  app.dependency_overrides[get_current_user] = return_user
  payload: dict[str, Any] = {
    "amount": 100,
    "payer_id": userPayer.id,
    "payee_id": userPayee.id,
    "group_id": group.id
  }
  response = auth_client.post("/api/payment",json=payload)
  print(response)
  assert response.status_code == 200
  assert response.json()["amount"] == 100
  
def test_create_payment_with_current_user_not_in_group(auth_client: TestClient):
  userCurrent = UserFactory()
  group = GroupFactory()
  userPayer = UserFactory()
  userPayee = UserFactory()
  group.users.append(userPayee)
  group.users.append(userPayer)

  def return_user() -> dict[str,Any]:
    return userCurrent

  app.dependency_overrides[get_current_user] = return_user
  payload: dict[str, Any] = {
    "amount": 100,
    "payer_id": userPayer.id,
    "payee_id": userPayee.id,
    "group_id": group.id
  }
  response = auth_client.post("/api/payment",json=payload)
  print(response)
  assert response.status_code == 403
  assert response.json()["detail"] == "User not allowed this action"
  
  
def test_create_payment_with_payer_not_in_group(auth_client: TestClient):
  userCurrent = UserFactory()
  group = GroupFactory()
  userPayer = UserFactory()
  userPayee = UserFactory()
  group.users.append(userCurrent)
  group.users.append(userPayee)

  def return_user() -> dict[str,Any]:
    return userCurrent

  app.dependency_overrides[get_current_user] = return_user
  payload: dict[str, Any] = {
    "amount": 100,
    "payer_id": userPayer.id,
    "payee_id": userPayee.id,
    "group_id": group.id
  }
  response = auth_client.post("/api/payment",json=payload)
  print(response)
  assert response.status_code == 400
  assert response.json()["detail"] == "Users not in group"
  
  
def test_create_payment_with_payee_not_in_group(auth_client: TestClient):
  userCurrent = UserFactory()
  group = GroupFactory()
  userPayer = UserFactory()
  userPayee = UserFactory()
  group.users.append(userCurrent)
  group.users.append(userPayer)

  def return_user() -> dict[str,Any]:
    return userCurrent

  app.dependency_overrides[get_current_user] = return_user
  payload: dict[str, Any] = {
    "amount": 100,
    "payer_id": userPayer.id,
    "payee_id": userPayee.id,
    "group_id": group.id
  }
  response = auth_client.post("/api/payment",json=payload)
  print(response)
  assert response.status_code == 400
  assert response.json()["detail"] == "Users not in group"
  
  
def test_create_payment_with_malformed_data(auth_client: TestClient):
  userCurrent = UserFactory()
  group = GroupFactory()
  userPayer = UserFactory()
  userPayee = UserFactory()
  group.users.append(userCurrent)
  group.users.append(userPayee)
  group.users.append(userPayer)

  def return_user() -> dict[str,Any]:
    return userCurrent


  app.dependency_overrides[get_current_user] = return_user
  payload: dict[str, Any] = {
    "payer_id": userPayer.id,
    "payee_id": userPayee.id,
    "group_id": group.id
  }
  response = auth_client.post("/api/payment",json=payload)
  assert response.status_code == 422
  