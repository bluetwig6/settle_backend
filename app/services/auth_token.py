from app.interfaces.services.auth_token import IAuthTokenService
from app.models import User, Token, TokenData
from fastapi import HTTPException, status
from datetime import timedelta, timezone, datetime
from typing import Any
from jwt.exceptions import InvalidTokenError
import jwt


class AuthTokenService(IAuthTokenService):
    
    def __init__(
    self, secret_key: str, token_expiration_minutes: int, algorithm: str
) -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._token_expiration_minutes = token_expiration_minutes
        
    def generate_jwt_token(self, user: User) -> Token:
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        expires_delta = timedelta(minutes=self._token_expiration_minutes)
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode:dict[str, Any] = {"sub": user.username, "exp": expire}
        encoded_jwt = jwt.encode(to_encode, self._secret_key, algorithm=self._algorithm)
            
        return Token(access_token=encoded_jwt, token_type="bearer")
    
    async def parse_jwt_token(self, token: str) -> dict[str, Any]:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
            username = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except InvalidTokenError:
            raise credentials_exception
        if not token_data.username:
            raise credentials_exception
        return payload