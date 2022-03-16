import json

from bots.groupme.groupme_helpers import send_message
from bots.helpers import ShowView
from bots.common.helpers import non_slash


def handle_groupme(request) -> bool:
    """Handles groupme bot inputs

    Parameters
    ----------
    request : Request
        The request object provided by FASTAPI

    Returns
    ----------
    success : bool
        Whether the response was sent successfully
    """

    req = json.loads(request.decode("utf-8"))
    text = req.get("text").strip()
    group_id = req.get("group_id").strip()
    response = non_slash(
        text,
        lambda x: send_message(x, group_id),
        lambda x, y, z: ShowView().groupme(x, group_id, y, **z),
    )
    return response
