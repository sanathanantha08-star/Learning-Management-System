from fastapi import APIRouter,status,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db


from src.users.schemas import RegisterResponse,RegisterRequest,UserOut
from src.users.service import UserService

router=APIRouter()
user_service=UserService()

@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)

async def register(payload:RegisterRequest,db: AsyncSession = Depends(get_db),) -> RegisterResponse:
    user=await user_service.register(db,payload)
    return RegisterResponse(
        message="Account created successfully.",
        user=UserOut.model_validate(user),
    )

