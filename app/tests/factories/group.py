# type: ignore

from ast import Tuple
from typing import Any, Dict

import factory
from app.config import get_app_settings
from app.models import Group
settings = get_app_settings()


class GroupFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta: # type: ignore
        model = Group # SQLAlchemy model
        sqlalchemy_session_persistence = "commit" # Commit the session after creating the user instance.
    
    name = factory.faker.Faker("sentence", nb_words=3)