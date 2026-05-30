from pydantic import BaseModel, Field
import uuid
from datetime import datetime

class CreateSectionRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    order_index: int = Field(..., ge=0)

class SectionOut(BaseModel):
    id: uuid.UUID
    course_id: uuid.UUID
    title: str
    order_index: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class CreateSectionResponse(BaseModel):
    message: str
    section: SectionOut