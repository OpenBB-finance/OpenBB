"""OpenBB API Account Router."""

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBasic
from openbb_core.api.dependency.user import get_current_username
from typing_extensions import Annotated

security = HTTPBasic()

router = APIRouter(prefix="/user", tags=["User"])
auth_hook = get_current_username


@router.get("/me")
def read_current_user(username: Annotated[str, Depends(get_current_username)]):
    return {"username": username}
