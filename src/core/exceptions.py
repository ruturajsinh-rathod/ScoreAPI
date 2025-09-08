from typing import Optional

from fastapi import status
from httpx import Response

from src import constants


class CustomException(Exception):
    """
    A custom exception class to raise necessary exceptions in the app.
    """

    status_code = status.HTTP_400_BAD_REQUEST
    message = constants.SOMETHING_WENT_WRONG

    def __init__(self, message: Optional[str] = None):
        if message:
            self.message = message


class BadRequestError(CustomException):
    """
    Custom exception for representing a Bad Request (HTTP 400) error.
    """

    status_code = status.HTTP_400_BAD_REQUEST


class UnauthorizedError(CustomException):
    """
    Custom exception for representing an Unauthorized (HTTP 401) error.
    """

    status_code = status.HTTP_401_UNAUTHORIZED


class ForbiddenError(CustomException):
    """
    Custom exception for representing a Forbidden (HTTP 403) error.
    """

    status_code = status.HTTP_403_FORBIDDEN


class NotFoundError(CustomException):
    """
    Custom exception for representing a Not Found (HTTP 404) error.
    """

    status_code = status.HTTP_404_NOT_FOUND


class AlreadyExistsError(CustomException):
    """
    Custom exception for representing a Conflict (HTTP 409) error indicating that the resource already exists.
    """

    status_code = status.HTTP_409_CONFLICT


class UnprocessableEntityError(CustomException):
    """
    Custom exception for representing an Unprocessable Entity (HTTP 422) error.
    """

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY


class InvalidJWTTokenException(CustomException):
    """
    Custom exception for representing an Unauthorized (HTTP 401) error due to an invalid JWT token.
    """

    status_code = status.HTTP_401_UNAUTHORIZED


class UnexpectedResponse(Exception):
    """
    Exception raised for an unexpected HTTP response.
    """

    def __init__(self, response: Response):
        self.response = response
