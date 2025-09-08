from src import constants
from src.core.exceptions import AlreadyExistsError, NotFoundError, UnauthorizedError


class InvalidCredsException(UnauthorizedError):
    """
    Raised when the provided login credentials are invalid.
    """

    message = constants.INVALID_CRED


class UnauthorizedAccessException(UnauthorizedError):
    """
    Raised when a user attempts to access a resource they are not authorized for.
    """

    message = constants.UNAUTHORIZEDACCESS
