"""Government of Canada Router."""

from openbb_core.app.router import Router

router = Router(prefix="")


@router.command(methods=["GET"])
async def available_indicators() -> list[dict]:
    """List the curated StatsCan indicators/tables from the shipped catalog."""
    # pylint: disable=import-outside-toplevel
    from openbb_government_ca.utils.catalog import CatalogReader

    return CatalogReader().indicators()
