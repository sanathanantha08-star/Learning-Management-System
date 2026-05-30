from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from src.database import get_db
from src.users.models import User
from src.users.dependencies import require_teacher
from src.sections.schemas import CreateSectionRequest as SectionCreate, CreateSectionResponse
from src.sections.service import SectionService

router = APIRouter()

section_service = SectionService()


@router.post(
    "/{course_id}/sections",
    response_model=CreateSectionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_section(
    course_id: uuid.UUID,
    data: SectionCreate,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
) -> CreateSectionResponse:
    return await section_service.create_section(db, course_id, data)