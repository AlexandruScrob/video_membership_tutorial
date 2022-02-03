from fastapi import HTTPException


class LoginRequiredException(HTTPException):
    """
    Login required
    """


class InvalidUserIDException(Exception):
    """
    Invalid User id
    """


class UserHasAccountException(Exception):
    """
    User already has account.
    """


class InvalidEmailException(Exception):
    """
    Invalid Email
    """
