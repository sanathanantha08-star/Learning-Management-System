from unittest import result
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.courses.models import Course
from src.core.retry.decorator import with_retry


class CourseRepository:

    @with_retry()
    async def create(self, db: AsyncSession, course: Course) -> Course:
        db.add(course)
        await db.flush()
        await db.refresh(course)
        return course

    @with_retry()
    async def get_by_teacher(self, db: AsyncSession, teacher_id: uuid.UUID) -> list[Course]:
        result = await db.execute(
            select(Course)
            .where(Course.teacher_id == teacher_id)
            .order_by(Course.created_at.desc())
        )
        return list(result.scalars().all())
    
    @with_retry()
    async def get_by_id(self, db: AsyncSession, course_id: uuid.UUID) -> Course | None:
        result = await db.execute(select(Course).where(Course.id == course_id))
        return result.scalar_one_or_none()

    @with_retry()
    async def update(self, db: AsyncSession, course: Course) -> Course:
        await db.flush()
        await db.refresh(course)
        return course
    
    