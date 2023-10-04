import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from openbb_core.env import Env
from typing_extensions import Annotated

security = HTTPBasic()


def get_current_username(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    current_username_bytes = credentials.username.encode("utf8")
    username = Env().ADMIN_USERNAME
    password = Env().ADMIN_PASSWORD

    is_correct_username = False
    is_correct_password = False

    if username is not None and password is not None:
        correct_username_bytes = username.encode("utf8")
        is_correct_username = secrets.compare_digest(
            current_username_bytes, correct_username_bytes
        )
        current_password_bytes = credentials.password.encode("utf8")
        correct_password_bytes = password.encode("utf8")
        is_correct_password = secrets.compare_digest(
            current_password_bytes, correct_password_bytes
        )

    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
