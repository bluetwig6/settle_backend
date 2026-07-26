from datetime import datetime
from typing import List

from sqlmodel import Session, select, delete

from app.interfaces.repositories.passwordResetToken import IPasswordResetTokenRepository
from app.models import PasswordResetToken

class PasswordResetTokenRespository(IPasswordResetTokenRepository):
    
    async def save_token_hash(self, session: Session, user_id: int, token_hash: str, expiration_time: datetime) -> PasswordResetToken:
        db_object = PasswordResetToken(user_id=user_id, token_hash=token_hash, expires_at=expiration_time)
        session.add(db_object)
        session.commit()
        session.refresh(db_object)
        return db_object
    
    
    async def get_token_object_by_hash_or_none(self, session: Session, token_hash: str) -> PasswordResetToken | None:
        token_object = session.exec(select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)).first()
        return token_object
    
    async def get_all_tokens_for_user_id(self, session: Session, user_id: int) -> List[PasswordResetToken]:
        token_objects = session.exec(select(PasswordResetToken).where(PasswordResetToken.user_id == user_id)).all()
        return list(token_objects)
    
    async def delete_all_existing_tokens_for_user_id(self, session: Session, user_id: int) -> None:
        statement = delete(PasswordResetToken).where(PasswordResetToken.user_id == user_id) # type: ignore
        session.exec(statement)
        session.commit()
        
    async def delete_token_by_hash(self, session: Session, token_hash: str) -> bool:
        statement = delete(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash) # type: ignore
        result = session.exec(statement)
        session.commit()
        return result.rowcount > 0