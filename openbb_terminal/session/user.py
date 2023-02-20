from openbb_terminal.core.models.user import UserModel
from openbb_terminal.core.models.profile import ProfileModel

profile = ProfileModel(  # type: ignore
    token_type=None,
    token=None,
    uuid=None,
    email=None,
    username=None,
)

User = UserModel(  # type: ignore
    profile=profile,
    configurations=None,
    preferences=None,
    credentials=None,
)
