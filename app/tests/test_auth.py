from fastapi.testclient import TestClient

from app.main import app
from app.tests.factories.user import UserFactory

client = TestClient(app)

def test_successful_login():
  user =  UserFactory(password="customPassword")
  form_data: dict[str,str] = {"username": user.username, "password": "customPassword"}
  response = client.post('/api/users/token', data=form_data)
  print(response.json())
  assert response.json()
  
  
def test_login_with_incorrect_username():
  UserFactory(password="customPassword")
  form_data: dict[str,str] = {"username": "incorrect_username", "password": "customPassword"}
  response = client.post('/api/users/token', data=form_data)
  assert response.status_code == 404
  assert response.json()['detail'] == "Incorrect username or password"
  
def test_login_with_incorrect_password():
  user =  UserFactory(password="customPassword")
  form_data: dict[str,str] = {"username": user.username, "password": "wrongpassword"}
  response = client.post('/api/users/token', data=form_data)
  assert response.status_code == 404
  assert response.json()['detail'] == "Incorrect username or password"