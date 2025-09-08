import json

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src import constants
from src.core.exceptions import CustomException, UnexpectedResponse


def start_exception_handlers(_app: FastAPI) -> None:
    """
    Defining Exception Handlers.
    """

    @_app.exception_handler(RequestValidationError)
    async def validation_exception_handler(*args) -> JSONResponse:
        """
        Handler for all the :class:`RequestValidationError` raised within the apps.
        """
        exc = args[1]
        transformed_errors = [
            {
                (
                    error["loc"][1]
                    if "loc" in error and len(error["loc"]) > 1
                    else "message"
                ): error["msg"]
            }
            for error in exc.errors()
        ]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "status": constants.ERROR,
                "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "message": transformed_errors,
            },
        )

    @_app.exception_handler(CustomException)
    async def custom_exception_handler(*args) -> JSONResponse:
        """
        Handler for all the :class:`CustomException` raised within the app.
        """
        exc = args[1]

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": constants.ERROR,
                "code": exc.status_code,
                "message": exc.message,
            },
        )

    @_app.exception_handler(UnexpectedResponse)
    async def unexpected_response(_request: Request, exc: UnexpectedResponse):
        """Unexpected code handler"""
        return JSONResponse(
            status_code=exc.response.status_code,
            content={
                "status": constants.ERROR,
                "code": exc.response.status_code,
                "message": json.loads(exc.response.content),
            },
        )
