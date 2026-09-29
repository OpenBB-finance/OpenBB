"""Registry for OBBjects."""

from typing import Any

from openbb_core.app.model.obbject import OBBject


class Registry:
    """Registry for OBBjects."""

    def __init__(self):
        """Initialize the registry."""
        self._obbjects: list[OBBject] = []

    @staticmethod
    def _contains_obbject(uuid: str, obbjects: list[OBBject]) -> bool:
        """Check if obbject with uuid is in the registry."""
        return any(obbject.id == uuid for obbject in obbjects)

    def register(self, obbject: OBBject) -> bool:
        """Designed to add an OBBject instance to the registry."""
        if (
            isinstance(obbject, OBBject)
            and not self._contains_obbject(obbject.id, self._obbjects)
            and obbject.results is not None
        ):
            self._obbjects.append(obbject)
            return True
        return False

    def get(self, arg: int | str) -> OBBject | None:
        """Return the obbject with index or key."""
        if isinstance(arg, int):
            return self._get_by_index(arg)
        if isinstance(arg, str):
            return self._get_by_key(arg)

        raise ValueError("Couldn't get the `OBBject` with the provided argument.")

    def _get_by_key(self, key: str) -> OBBject | None:
        """Return the obbject with key."""
        for obbject in self._obbjects:
            if obbject.extra.get("register_key", "") == key:
                return obbject
        return None

    def _get_by_index(self, idx: int) -> OBBject | None:
        """Return the obbject at index idx."""
        reversed_list = list(reversed(self._obbjects))

        if idx >= len(reversed_list):
            return None

        return reversed_list[idx]

    def remove(self, idx: int = -1):
        """Remove the obbject at index idx, default is the last element."""
        reversed_list = list(reversed(self._obbjects))
        del reversed_list[idx]
        self._obbjects = list(reversed(reversed_list))

    @property
    def all(self) -> dict[int, dict]:
        """Return all obbjects in the registry."""
        obbjects: dict[int, dict] = {}
        for i, obbject in enumerate(list(reversed(self._obbjects))):
            model_dump = getattr(obbject, "model_dump", None)
            dump: dict[str, Any] | None = None
            if callable(model_dump):
                try:
                    candidate = model_dump(exclude={"results"})
                except Exception:  # noqa: BLE001
                    candidate = None
                if isinstance(candidate, dict):
                    dump = candidate
            if dump is None:
                dump = {
                    "id": getattr(obbject, "id", None),
                    "provider": getattr(obbject, "provider", None),
                    "warnings": getattr(obbject, "warnings", None),
                    "chart": getattr(obbject, "chart", None),
                    "extra": getattr(obbject, "extra", {}) or {},
                }
            obbjects[i] = dump

        return obbjects

    @property
    def obbjects(self) -> list[OBBject]:
        """Return all obbjects in the registry."""
        return self._obbjects

    @property
    def obbject_keys(self) -> list[str]:
        """Return all obbject keys in the registry."""
        return [
            obbject.extra["register_key"]
            for obbject in self._obbjects
            if "register_key" in obbject.extra
        ]
