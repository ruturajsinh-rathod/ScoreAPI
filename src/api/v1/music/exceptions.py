from src import constants
from src.core.exceptions import AlreadyExistsError, NotFoundError, UnauthorizedError


class InvalidCredsException(UnauthorizedError):
    """
    Raised when the provided login credentials are invalid.
    """

    message = constants.INVALID_CRED
