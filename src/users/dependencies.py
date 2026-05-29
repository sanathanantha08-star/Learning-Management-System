from fastapi.security import OAuth2PasswordBearer

from fastapi import Depends
from src.core.errors.codes import ErrorCode
from src.core.errors.exceptions import UnauthorizedException
from src.users.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.users.models import User
from jose import ExpiredSignatureError, JWTError, jwt
from src.config import get_settings
from src.users.repository import UserRepository

from src.core.errors.exceptions import UnauthorizedException
from src.core.errors.codes import ErrorCode
settings = get_settings()
repo=UserRepository()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")#instead of manually extracting the bearer token from the header, we can use this dependency to do it for us. It will look for the Authorization header and extract the token for us.
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    try:#decoding the token and extracting the user id and token type from the payload. If the token is expired or invalid, it raises an UnauthorizedException with the appropriate error code and message. Then it retrieves the user from the database using the user id and checks if the user exists and is active. If not, it raises an UnauthorizedException with the appropriate error code and message. Finally, it returns the user object.
        payload=jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id:str=payload.get("sub")
        token_type:str=payload.get("type")
        if not user_id or token_type != "access":
            raise UnauthorizedException(
                code=ErrorCode.AUTH_TOKEN_INVALID,
                detail="Invalid token.",
            )
    except ExpiredSignatureError:
        raise UnauthorizedException(
            code=ErrorCode.AUTH_TOKEN_EXPIRED,
            detail="Access token has expired.",
        )
    
    except JWTError:
        raise UnauthorizedException(
            code=ErrorCode.AUTH_TOKEN_INVALID,
            detail="Invalid token.",
        )
    
    user=await repo.get_by_id(db, user_id)#extracting and returnign user from the database using the user id obtained from the token payload. If the user is not found or is inactive, it raises an UnauthorizedException with the appropriate error code and message. Finally, it returns the user object.
    if not user:
        raise UnauthorizedException(
            code=ErrorCode.USR_NOT_FOUND,
            detail="User not found.",
        )
    if not user.is_active:
        raise UnauthorizedException(
            code=ErrorCode.USR_INACTIVE,
            detail="User is inactive.",
        )
    return user

async def require_teacher(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "teacher":
        raise UnauthorizedException(
            code=ErrorCode.AUTH_INSUFFICIENT_ROLE,
            detail="User does not have the required role.",
        )
    return current_user

async def required_student(
        current_user:User=Depends(get_current_user),
)->User:
    if current_user.role!="student":
        raise UnauthorizedException(
            code=ErrorCode.AUTH_INSUFFICIENT_ROLE,
            detail="User does not have the required role.",
        )
    return current_user