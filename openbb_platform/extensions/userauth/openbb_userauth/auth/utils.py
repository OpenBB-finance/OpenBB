from datetime import datetime, timedelta
from typing import Optional

from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from openbb_core.api.model.access_token import AccessToken
from openbb_core.app.model.user_settings import UserSettings
from passlib.context import CryptContext

from openbb_userauth.user.userdb_service import UserDBService

# ruff: noqa: S105
SECRET_KEY = "a0657288545d1d2e991195841782ae2a22574a22954081db0c2888c5f5ddbecc"  # nosec # pragma: allowlist secret
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440
TOKEN_URL = "/api/v1/user/token"


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=TOKEN_URL)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    """Verify password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Get password hash."""
    return pwd_context.hash(password)


def authenticate_user(
    password: str,
    username: str,
    userdb_service: UserDBService,
) -> Optional[UserSettings]:
    """Authenticate user."""
    user = userdb_service.user_settings_repository.read_by_profile(
        filter_list=[("username", username)],
    )
    if (
        user
        and user.profile
        and user.profile.password_hash
        and verify_password(password, user.profile.password_hash)
    ):
        return user

    return None


def create_access_token(
    sub: str,
    expiration_delta: Optional[timedelta] = None,
) -> AccessToken:
    """Create access token."""
    if expiration_delta is None:
        expiration_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    expiration_datetime = datetime.utcnow() + expiration_delta
    return AccessToken(
        sub=sub,
        exp=expiration_datetime,
    )


def create_jwt_token(
    access_token: AccessToken,
    key=SECRET_KEY,
    algorithm=ALGORITHM,
) -> str:
    """Create JWT token."""
    claims = access_token.model_dump()
    encoded_jwt = jwt.encode(claims=claims, key=key, algorithm=algorithm)
    return encoded_jwt
