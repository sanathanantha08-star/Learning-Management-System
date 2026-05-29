from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.courses.schemas import CreateCourseRequest, CreateCourseResponse, TeacherCoursesResponse,CourseUpdateRequest, CourseUpdateResponse
from src.courses.service import CourseService
from src.database import get_db
from src.users.dependencies import require_teacher
from src.users.models import User
import uuid

router = APIRouter()
course_service = CourseService()

@router.post(
    "",
    response_model=CreateCourseResponse,
    status_code=status.HTTP_201_CREATED,
)

async def create_course(
    data: CreateCourseRequest,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
) -> CreateCourseResponse:
    return await course_service.create_course(data, current_user, db)


@router.get(
    "/me",
    response_model=TeacherCoursesResponse,
    status_code=status.HTTP_200_OK,
)
async def get_teacher_courses(
   teacher: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
) -> TeacherCoursesResponse:
    return await course_service.get_teacher_courses(db, teacher)


@router.put(
    "/{course_id}",
    response_model=CourseUpdateResponse,
    status_code=status.HTTP_200_OK,
)

async def update_course(
    course_id: uuid.UUID,
    payload: CourseUpdateRequest,
    teacher: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
) -> CourseUpdateResponse:
    return await course_service.update_course(db, teacher, course_id, payload)
