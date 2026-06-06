import abc

from app.models import User,Token
from typing import Any

class IAuthTokenService(abc.ABC):
    @abc.abstractmethod
    def generate_jwt_token(self, user: User) -> Token: ...

    @abc.abstractmethod
    async def parse_jwt_token(self, token: str) -> dict[str, Any]: ...
