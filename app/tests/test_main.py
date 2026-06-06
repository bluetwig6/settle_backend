from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    print(response)
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
    
    
def test_auth_read_main(auth_client: TestClient):
    response = auth_client.get("/")
    print(response)
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}