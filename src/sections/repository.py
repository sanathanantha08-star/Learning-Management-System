

import uuid

from src.core.retry.decorator import with_retry
from src.sections.models import Section
from src.sections.schemas import SectionOut

from sqlalchemy.ext.asyncio import AsyncSession

class SectionRepository:


    @with_retry()
    async def create(self, db: AsyncSession, section: Section) -> Section:
        db.add(section)
        await db.flush()
        await db.refresh(section)
        return section