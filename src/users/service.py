from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import hash_password, verify_password
from src.core.errors.codes import ErrorCode
from src.core.errors.exceptions import ConflictException, UnauthorizedException
from src.core.logger import get_logger
from src.users.models import RefreshToken, User
from src.users.repository import UserRepository
from src.users.schemas import LoginRequest, RegisterRequest, TokenResponse, LogoutRequest, LogoutResponse,  RefreshTokenOutRequest, RefreshTokenResponse, UpdateUserResponse,UpdateUserRequest, UserOut
from src.config import get_settings

import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from jose import jwt

logger = get_logger(__name__)
settings = get_settings()


class UserService:
    def __init__(self) -> None:
        self.repo = UserRepository()

    def _create_access_token(self, user_id: uuid.UUID, role: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )
        payload = {
            "sub": str(user_id),
            "role": role,
            "exp": expire,
            "type": "access",
        }
        return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    def _create_refresh_token(self) -> tuple[str, str]:
        raw = str(uuid.uuid4())
        hashed = hashlib.sha256(raw.encode()).hexdigest()
        return raw, hashed

    async def register(self, db: AsyncSession, data: RegisterRequest) -> User:
        existing = await self.repo.get_by_email(db, data.email)
        if existing:
            raise ConflictException(
                code=ErrorCode.AUTH_EMAIL_ALREADY_EXISTS,
                detail=f"An account with email '{data.email}' already exists.",
            )

        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            role=data.role,
        )
        created = await self.repo.create(db, user)
        logger.info("user_registered", user_id=str(created.id), role=created.role)
        return created

    async def login(self, db: AsyncSession, data: LoginRequest) -> TokenResponse:
        user = await self.repo.get_by_email(db, data.email)
        if not user:
            raise UnauthorizedException(
                code=ErrorCode.AUTH_INVALID_CREDENTIALS,
                detail="Invalid email or password.",
            )

        if not user.is_active:
            raise UnauthorizedException(
                code=ErrorCode.USR_INACTIVE,
                detail="This account has been deactivated.",
            )

        if not verify_password(data.password, user.hashed_password):
            raise UnauthorizedException(
                code=ErrorCode.AUTH_INVALID_CREDENTIALS,
                detail="Invalid email or password.",
            )

        access_token = self._create_access_token(user.id, user.role)
        raw_refresh, hashed_refresh = self._create_refresh_token()

        refresh_token_obj = RefreshToken(
            user_id=user.id,
            token_hash=hashed_refresh,
            expires_at=datetime.now(timezone.utc) + timedelta(
                days=settings.jwt_refresh_token_expire_days
            ),
        )
        await self.repo.create_refresh_token(db, refresh_token_obj)

        logger.info("user_logged_in", user_id=str(user.id), role=user.role)

        return TokenResponse(
            access_token=access_token,
            refresh_token=raw_refresh,
        )
    
    async def logout(self,db: AsyncSession, data: LogoutRequest) -> LogoutResponse:
        token_hash = hashlib.sha256(data.refresh_token.encode()).hexdigest()
        token = await self.repo.get_refresh_token_by_hash(db, token_hash)
        if not token:
            raise UnauthorizedException(
                code=ErrorCode.AUTH_REFRESH_TOKEN_INVALID,
                detail="Invalid refresh token.",
            )
        if token.revoked:
            raise UnauthorizedException(
                code=ErrorCode.AUTH_REFRESH_TOKEN_INVALID,
                detail="Refresh token already revoked.",
            )
        await self.repo.revoke_refresh_token(db, token_hash)
        logger.info("user_logged_out", user_id=str(token.user_id))
        return LogoutResponse(message="Logged out successfully.")
    

    async def refresh_access_token(self,db:AsyncSession,data:RefreshTokenOutRequest) -> RefreshTokenResponse:
        token=await self.repo.get_refresh_token_by_hash(db, hashlib.sha256(data.refresh_token.encode()).hexdigest())
        if not token:
            raise UnauthorizedException(
                code=ErrorCode.AUTH_REFRESH_TOKEN_INVALID,
                detail="Refresh token not found.",
            )
    
        if not token.is_valid:
            raise UnauthorizedException(
                code=ErrorCode.AUTH_REFRESH_TOKEN_INVALID,
                detail="Refresh token is expired or revoked.",
            )
        user = await self.repo.get_by_id(db, token.user_id)
        if not user or not user.is_active:
            raise UnauthorizedException(
                code=ErrorCode.USR_INACTIVE,
                detail="User not found or inactive.",
            )
        access_token = self._create_access_token(user.id, user.role)
        logger.info("access_token_refreshed", user_id=str(user.id))
        return RefreshTokenResponse(access_token=access_token)
    

    async def update_user(self,db:AsyncSession,current_user:User,payload:UpdateUserRequest) -> UpdateUserResponse:
        if payload.full_name is not None:
            current_user.full_name = payload.full_name
        if payload.avatar_url is not None:
            current_user.avatar_url = payload.avatar_url
        updated_user = await self.repo.update_user(db, current_user)
        logger.info("profile_updated", user_id=str(updated_user.id))
        return UpdateUserResponse(
            message="User updated successfully.",
            user=UserOut.model_validate(updated_user),
        )