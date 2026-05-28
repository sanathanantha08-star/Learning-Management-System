from fastapi import APIRouter,status,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db


from src.users.schemas import LoginRequest, LogoutRequest, RegisterResponse,RegisterRequest, TokenResponse,UserOut,LogoutResponse,RefreshTokenOutRequest, RefreshTokenResponse
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



@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)

async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    return await user_service.login(db,payload)

@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
)
async def logout(payload: LogoutRequest, db: AsyncSession = Depends(get_db)) -> LogoutResponse:
    return await user_service.logout(db,payload)
    

@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    status_code=status.HTTP_200_OK,
)

async def refresh(payload: RefreshTokenOutRequest, db: AsyncSession = Depends(get_db)) -> RefreshTokenResponse:
    return await user_service.refresh_access_token(db,payload)