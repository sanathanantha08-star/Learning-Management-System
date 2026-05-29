import uuid
from datetime import datetime
from pydantic import BaseModel

class CreateCourseRequest(BaseModel):
    title: str
    description: str | None = None
    thumbnail_url: str | None = None


class CourseOut(BaseModel):
    id: uuid.UUID
    teacher_id: uuid.UUID
    title: str
    description: str | None = None
    thumbnail_url: str | None = None
    is_published: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class CreateCourseResponse(BaseModel):
    message: str
    course: CourseOut

class TeacherCoursesResponse(BaseModel):
    courses: list[CourseOut]
    total: int

class CourseUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    thumbnail_url: str | None = None
    is_published: bool | None = None

class CourseUpdateResponse(BaseModel):  
    message: str
    course: CourseOut
