from collections.abc import Callable
from typing import Any

from sqlalchemy.exc import OperationalError, TimeoutError
from tenacity import retry, retry_if_exception_type, stop_after_attempt

from src.core.logger import get_logger
from src.core.retry.stratergies import exponential_jitter

logger = get_logger(__name__)

RETRYABLE_EXCEPTIONS = (
    OperationalError,
    TimeoutError,
    ConnectionError,
    OSError,
)


def with_retry(attempts: int = 3, wait=None, reraise: bool = True) -> Callable:
    if wait is None:
        wait = exponential_jitter(max_wait=5)

    def decorator(func: Callable) -> Callable:
        @retry(
            stop=stop_after_attempt(attempts),
            wait=wait,
            retry=retry_if_exception_type(RETRYABLE_EXCEPTIONS),
            reraise=reraise,
            before_sleep=_log_retry_attempt,
        )
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await func(*args, **kwargs)
        return wrapper

    return decorator


def _log_retry_attempt(retry_state) -> None:
    logger.warning(
        "retrying_db_call",
        attempt=retry_state.attempt_number,
        fn=retry_state.fn.__name__ if retry_state.fn else "unknown",
        wait_seconds=round(retry_state.next_action.sleep, 2) if retry_state.next_action else None,
        exc=str(retry_state.outcome.exception()) if retry_state.outcome else None,
    )