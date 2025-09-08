from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from config.config import basic_auth_settings
from src.api.v1.music.exceptions import InvalidCredsException


def basic_auth(credentials: HTTPBasicCredentials = Depends(HTTPBasic())):
    """
    Dependency function for required basic authentication.
    It uses the HTTPBasic instance to perform authentication.

    Args:
    - credentials: HTTPBasicCredentials object containing the provided username and password.

    Returns:
    - True if authentication is successful.

    Raises:
    - InvalidCredsException: If authentication fails.
    """

    if (
        credentials.username == basic_auth_settings.BASIC_USERNAME
        and credentials.password == basic_auth_settings.BASIC_PASSWORD
    ):
        return True
    else:
        raise InvalidCredsException
