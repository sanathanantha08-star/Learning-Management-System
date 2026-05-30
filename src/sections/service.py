
from src.core.errors.codes import ErrorCode
from src.core.errors.exceptions import NotFoundException
from src.courses.repository import CourseRepository
from src.sections.models import Section
from src.sections.repository import SectionRepository
from src.sections.schemas import CreateSectionRequest, CreateSectionResponse, SectionOut
from src.users.models import User
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from src import courses
from src.core.errors.exceptions import NotFoundException
from src.courses.repository import CourseRepository
from src.sections.models import Section
from src.sections.repository import SectionRepository
from src.sections.schemas import CreateSectionRequest, CreateSectionResponse, SectionOut
from src.users.models import User
from sqlalchemy.ext.asyncio import AsyncSession
import uuid


class SectionService:
    def __init__(self):
        self.repo = SectionRepository()
        self.course_repo = CourseRepository()

    async def create_section(self,db:AsyncSession, course_id: uuid.UUID, payload:CreateSectionRequest) -> CreateSectionResponse:
        course = await self.course_repo.get_by_id(db, course_id)
        if not course:
            raise NotFoundException(
                code=ErrorCode.CRS_NOT_FOUND,
                detail="Course not found.",
            )
        section = Section(
            course_id=course_id,
            title=payload.title,
            order_index=payload.order_index,
        )
        created = await self.repo.create(db, section)
        return CreateSectionResponse(
            message="Section created successfully.",
            section=SectionOut.model_validate(created),
        )
        