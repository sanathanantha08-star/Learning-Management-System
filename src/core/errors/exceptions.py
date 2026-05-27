from dataclasses import dataclass, field
from typing import Any

from starlette.status import HTTP_400_BAD_REQUEST

from src.core.errors.codes import ErrorCode


@dataclass
class AppException(Exception):
    code: ErrorCode
    status_code: int = HTTP_400_BAD_REQUEST
    detail: str = ""
    context: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"[{self.code}] {self.detail}"


class NotFoundException(AppException):
    def __init__(self, code: ErrorCode, detail: str, **context: Any) -> None:
        super().__init__(code=code, status_code=404, detail=detail, context=context)


class UnauthorizedException(AppException):
    def __init__(self, code: ErrorCode, detail: str, **context: Any) -> None:
        super().__init__(code=code, status_code=401, detail=detail, context=context)


class ForbiddenException(AppException):
    def __init__(self, code: ErrorCode, detail: str, **context: Any) -> None:
        super().__init__(code=code, status_code=403, detail=detail, context=context)


class ConflictException(AppException):
    def __init__(self, code: ErrorCode, detail: str, **context: Any) -> None:
        super().__init__(code=code, status_code=409, detail=detail, context=context)