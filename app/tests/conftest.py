from typing import Any, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session
from app.config import get_app_settings
from app.main import app
from app.core.dependecies import engine, get_session
from app.tests.factories.group import GroupFactory
from app.tests.factories.user import UserFactory

def create_test_database() -> None:
    SQLModel.metadata.create_all(engine)
  
def drop_db_and_tables():
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
  create_test_database()
  yield
  drop_db_and_tables()
  
@pytest.fixture
def current_user() -> dict[str, Any]:
    return {"username": "testuser", "id": 1}

@pytest.fixture
def auth_client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Forces FastAPI to use the exact same database session as our factories,
    then injects auth headers.
    """
    def _override_get_session():
        try:
            yield db_session
        finally:
            pass  # The db_session fixture handles closing, don't close it here

    # Override the app's internal DB dependency
    app.dependency_overrides[get_session] = _override_get_session
    
    with TestClient(app) as client:
        client.headers.update({"Authorization": "Bearer testtoken"})
        yield client
        
    # Clean up overrides after the test finishes
    app.dependency_overrides.clear()
  
@pytest.fixture
def oauth2_scheme() -> str:
  return 'testtoken'

settings = get_app_settings()
engine_props = settings.sqlalchemy_engine_props
engine = create_engine(engine_props["url"], echo=engine_props["echo"])

@pytest.fixture
def db_session() -> Generator[Session, None, None]:
  connection = engine.connect()
  transaction = connection.begin()
  with Session(bind=connection) as session:
      yield session
  
  session.close()
  transaction.rollback()
  connection.close()
  
@pytest.fixture(autouse=True)
def set_session_for_factories(db_session: Session):
    UserFactory._meta.sqlalchemy_session = db_session # type: ignore
    GroupFactory._meta.sqlalchemy_session = db_session # type: ignore
    yield 