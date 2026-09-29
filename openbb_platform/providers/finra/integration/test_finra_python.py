"""FINRA through the Python interface, against the live services."""

import pytest
from openbb_core.app.model.obbject import OBBject

from .cases import COMMANDS, case_id, path

pytestmark = pytest.mark.integration


def _command(obb, command: str, owner: str | None):
    """Return the Python command for a route, wherever it is served."""
    target = obb

    for part in path(command, owner):
        target = getattr(target, part)

    return target


class TestCommands:
    """Every command returns rows."""

    @pytest.mark.parametrize("case", COMMANDS, ids=case_id)
    def test_returns_rows(self, obb, case):
        """The command answers with an OBBject holding at least one row."""
        command, owner, params = case
        result = _command(obb, command, owner)(provider="finra", **params)

        assert isinstance(result, OBBject)
        assert result.provider == "finra"
        assert result.results

    def test_history_converts_to_a_frame(self, obb):
        """The end-of-day history converts to a DataFrame indexed by date."""
        frame = obb.finra.fixedincome.bond_historical(
            cusip="037833EH9", provider="finra"
        ).to_df()

        assert not frame.empty
        assert frame.index.name == "date"


class TestRefusals:
    """Queries FINRA cannot serve are refused before any request."""

    def test_unpublished_parameter(self, obb):
        """TRACE does not publish ISINs."""
        from openbb_core.app.model.abstract.error import OpenBBError

        with pytest.raises(OpenBBError, match="does not publish isin"):
            _command(obb, "fixedincome.bond_prices", "FIXEDINCOME_INSTALLED")(
                isin="US037833EH90", provider="finra"
            )
