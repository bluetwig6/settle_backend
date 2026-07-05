# type: ignore

from ast import Tuple
from typing import Any, Dict

import factory
from app.config import get_app_settings
from app.models import Item
settings = get_app_settings()


class ItemFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta: # type: ignore
        model = Item # SQLAlchemy model
        sqlalchemy_session_persistence = "commit" # Commit the session after creating the user instance.
    
    title = factory.faker.Faker("sentence", nb_words=1)
    amount = factory.faker.Faker('pyint', min_value=0, max_value=1000)