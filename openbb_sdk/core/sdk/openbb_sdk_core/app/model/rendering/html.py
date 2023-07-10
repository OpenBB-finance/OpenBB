from pydantic import Field

from openbb_sdk_core.app.model.abstract.rendering import ContentKind, Rendering


class HTML(Rendering):
    content_kind: ContentKind = Field(default=ContentKind.html, allow_mutation=False)

    class Config:
        validate_assignment = True
