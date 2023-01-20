from typing import Optional


class User:
    token_type: str = ""
    token: str = ""
    email: str = ""
    uuid: str = ""
    configs: Optional[dict] = None
