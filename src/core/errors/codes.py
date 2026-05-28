from enum import Enum


class ErrorCode(str, Enum):
    # Auth
    AUTH_INVALID_CREDENTIALS   = "AUTH_001"
    AUTH_TOKEN_EXPIRED         = "AUTH_002"
    AUTH_TOKEN_INVALID         = "AUTH_003"
    AUTH_REFRESH_TOKEN_INVALID = "AUTH_004"
    AUTH_INSUFFICIENT_ROLE     = "AUTH_005"
    AUTH_EMAIL_ALREADY_EXISTS  = "AUTH_006"

    # Users
    USR_NOT_FOUND              = "USR_001"
    USR_INACTIVE               = "USR_002"
    USR_INVALID_PASSWORD       = "USR_003"
    INTERNAL_ERROR             = "GEN_001"
    VALIDATION_ERROR           = "GEN_002"