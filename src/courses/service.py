from sqlalchemy.ext.asyncio import AsyncSession

from src.core.errors.codes import ErrorCode
from src.core.errors.exceptions import NotFoundException
from src.courses.models import Course
from src.courses.repository import CourseRepository
from src.courses.schemas import CourseUpdateRequest,CourseUpdateResponse, CreateCourseRequest, CreateCourseResponse, CourseOut, TeacherCoursesResponse
from src.users.models import User
from src.core.logger import get_logger
import uuid

logger = get_logger(__name__)

class CourseService:
    def __init__(self) -> None:
        self.repo = CourseRepository()

    async def create_course(self, data: CreateCourseRequest, current_user: User, db: AsyncSession) -> CreateCourseResponse:
        course=Course(
            teacher_id=current_user.id,
            title=data.title,
            description=data.description,
            thumbnail_url=data.thumbnail_url,

        )
        created=await self.repo.create(db,course)
        logger.info("course_created", course_id=str(created.id), teacher_id=str(current_user.id))
        return CreateCourseResponse(
            message="Course created successfully.",
            course=CourseOut.model_validate(created),
        )
    
    async def get_teacher_courses(self,db:AsyncSession,teacher: User) -> TeacherCoursesResponse:
        courses=await self.repo.get_by_teacher(db,teacher.id)
        return TeacherCoursesResponse(
            courses=[CourseOut.model_validate(course) for course in courses],
            total=len(courses)
        )
    
    async def update_course(self,db:AsyncSession,teacher:User,course_id:uuid.UUID,payload:CourseUpdateRequest) -> CourseUpdateResponse:
        course=await self.repo.get_by_id(db,course_id)
        if not course:
            raise NotFoundException(
            code=ErrorCode.CRS_NOT_FOUND,
            detail="Course not found.",
            )

        if course.teacher_id != teacher.id:
            raise NotFoundException(
            code=ErrorCode.CRS_NOT_OWNER,
            detail="Course not found.",
        )
        if payload.title is not None:
            course.title=payload.title
        if payload.description is not None:
            course.description=payload.description
        if payload.thumbnail_url is not None:
            course.thumbnail_url=payload.thumbnail_url
        if payload.is_published is not None:
            course.is_published=payload.is_published
        updated=await self.repo.update(db,course)
        logger.info("course_updated", course_id=str(course.id), teacher_id=str(teacher.id))
        return CourseUpdateResponse(
            message="Course updated successfully.",
            course=CourseOut.model_validate(updated),
        )