from passlib.context import CryptContext
from src.core.logger import get_logger
from src.core.security import (
    hash_password,
    verify_password,
)

from src.users.repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from src.users.schemas import RegisterRequest
from src.users.models import User
from src.core.errors.codes import ErrorCode
from src.core.errors.exceptions import ConflictException

logger = get_logger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService():
    def __init__(self)->None:
        self.repo=UserRepository()


    async def register(self,db:AsyncSession,data:RegisterRequest)->User:
        existing = await self.repo.get_by_email(db, data.email)
        if existing:
            
            raise ConflictException(
                code=ErrorCode.AUTH_EMAIL_ALREADY_EXISTS,
                detail=f"An account with email '{data.email}' already exists.",
            )
        user=User(
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.ful_name,
            role=data.role



        )
        created = await self.repo.create(db, user)
        logger.info("user_registered", user_id=str(created.id), role=created.role)
        return created
