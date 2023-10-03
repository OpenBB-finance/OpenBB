"""OpenBB API Account Router."""
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing_extensions import Annotated

security = HTTPBasic()

router = APIRouter(prefix="/user", tags=["User"])
auth_hook = lambda: None


@router.get("/me")
def read_current_user(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    return {"username": credentials.username, "password": credentials.password}
