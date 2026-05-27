import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import User, RefreshToken
from src.core.retry.decorator import with_retry


class UserRepository:

    # ── User queries ──────────────────────────────────────────────────────────

    @with_retry()
    async def get_by_id(self, db: AsyncSession, user_id: uuid.UUID) -> User | None:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @with_retry()
    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @with_retry()
    async def create(self, db: AsyncSession, user: User) -> User:
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user

    # ── Refresh token queries ─────────────────────────────────────────────────

    @with_retry()
    async def create_refresh_token(self, db: AsyncSession, token: RefreshToken) -> RefreshToken:
        db.add(token)
        await db.flush()
        await db.refresh(token)
        return token

    @with_retry()
    async def get_refresh_token_by_hash(self, db: AsyncSession, token_hash: str) -> RefreshToken | None:
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        return result.scalar_one_or_none()

    @with_retry()
    async def revoke_refresh_token(self, db: AsyncSession, token_hash: str) -> None:
        token = await self.get_refresh_token_by_hash(db, token_hash)
        if token:
            token.revoked = True
            await db.flush()

    @with_retry()
    async def revoke_all_user_tokens(self, db: AsyncSession, user_id: uuid.UUID) -> None:
        result = await db.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked == False,
            )
        )
        for token in result.scalars().all():
            token.revoked = True
        await db.flush()