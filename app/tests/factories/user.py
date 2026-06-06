# type: ignore

from ast import Tuple
from typing import Any, Dict

import factory
from app.config import get_app_settings
from app.models import User
from app.services.password import get_password_hash
settings = get_app_settings()


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta: # type: ignore
        model = User # SQLAlchemy model
        sqlalchemy_session_persistence = "commit" # Commit the session after creating the user instance.
    
    username = factory.faker.Faker("name")
    email = factory.faker.Faker("email")
    hashed_password = factory.declarations.LazyFunction(
       lambda: get_password_hash(settings.jwt_secret_key)
    )
    
    
    @classmethod
    def _create(cls, model_class, *args, **kwargs) -> User: # type: ignore
        # Handle the password argument before creating the user
        if "password" in kwargs:
            kwargs["hashed_password"] = get_password_hash(kwargs.pop("password"))
        return super()._create(model_class, *args, **kwargs)