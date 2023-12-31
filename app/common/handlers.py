from fastapi import HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from http import HTTPStatus


class ErrorCode:
    UNAUTHORIZED_USER = "unauthorized_user"
    NETWORK_FAILURE = "network_failure"
    SERVER_ERROR = "server_error"
    INVALID_ENTRY = "invalid_entry"
    INCORRECT_EMAIL = "incorrect_email"
    INCORRECT_OTP = "incorrect_otp"
    EXPIRED_OTP = "expired_otp"
    INVALID_AUTH = "invalid_auth"
    INVALID_TOKEN = "invalid_token"
    INVALID_CREDENTIALS = "invalid_credentials"
    UNVERIFIED_USER = "unverified_user"
    NON_EXISTENT = "non_existent"
    INVALID_OWNER = "invalid_owner"
    INVALID_PAGE = "invalid_page"
    INVALID_VALUE = "invalid_value"
    NOT_ALLOWED = "not_allowed"
    INVALID_DATA_TYPE = "invalid_data_type"
    BAD_REQUEST = "bad_request"


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class RequestError(Error):
    def __init__(
        self,
        err_code: str,
        err_msg: str,
        status_code: int = 400,
        data: dict = None,
        *args: object,
    ) -> None:
        self.status_code = HTTPStatus(status_code)
        self.err_code = err_code
        self.err_msg = err_msg
        self.data = data

        super().__init__(*args)


def request_error_handler(request, exc: RequestError):
    err_dict = {
        "status": "failure",
        "code": exc.err_code,
        "message": exc.err_msg,
    }
    if exc.data:
        err_dict["data"] = exc.data
    return JSONResponse(status_code=exc.status_code, content=err_dict)


def http_exception_handler(request, exc):
    if isinstance(exc, HTTPException):
        return JSONResponse(
            content={"status": "failure", "message": exc.detail},
            status_code=exc.status_code,
        )


def validation_exception_handler(request, exc: RequestValidationError):
    # Get the original 'detail' list of errors
    details = exc.raw_errors[0].exc.errors()
    modified_details = {}
    for error in details:
        try:
            field_name = error["loc"][1]
        except:
            field_name = error["loc"][0]

        modified_details[f"{field_name}"] = error["msg"]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "failure",
            "message": "Invalid Entry",
            "data": modified_details,
        },
    )


def internal_server_error_handler(request, exc: Exception):
    print(exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "failure",
            "message": "Server Error",
        },
    )


exc_handlers = {
    HTTPException: http_exception_handler,
    RequestValidationError: validation_exception_handler,
    RequestError: request_error_handler,
    Exception: internal_server_error_handler,
}
