from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_500_INTERNAL_SERVER_ERROR

from src.core.errors.codes import ErrorCode
from src.core.errors.exceptions import AppException
from src.core.logger import get_logger

logger = get_logger(__name__)


def _error_response(
    status_code: int,
    error_code: ErrorCode | str,
    detail: str,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error_code": error_code.value if isinstance(error_code, ErrorCode) else error_code,
            "detail": detail,
        },
    )


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        logger.warning(
            "app_exception",
            error_code=exc.code,
            detail=exc.detail,
            status_code=exc.status_code,
            path=request.url.path,
            **exc.context,
        )
        return _error_response(exc.status_code, exc.code, exc.detail)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        messages = "; ".join(
            f"{' → '.join(str(l) for l in e['loc'])}: {e['msg']}"
            for e in exc.errors()
        )
        logger.info("validation_error", detail=messages, path=request.url.path)
        return _error_response(HTTP_422_UNPROCESSABLE_ENTITY, ErrorCode.VALIDATION_ERROR, messages)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_exception", exc_info=exc, path=request.url.path)
        return _error_response(
            HTTP_500_INTERNAL_SERVER_ERROR,
            ErrorCode.INTERNAL_ERROR,
            "An unexpected error occurred. Please try again later.",
        )