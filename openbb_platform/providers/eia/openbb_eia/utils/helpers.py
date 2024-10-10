"""OpenBB EIA Provider Module Helpers."""

from typing import TYPE_CHECKING

from async_lru import alru_cache

if TYPE_CHECKING:
    from pandas import ExcelFile


@alru_cache(maxsize=14)
async def download_excel_file(url: str, use_cache: bool = True) -> "ExcelFile":
    """Download the excel file from the URL. Set use_cache to False to invalidate the ALRU cache."""
    # pylint: disable=import-outside-toplevel
    from io import BytesIO  # noqa
    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.provider.utils.helpers import amake_request
    from pandas import ExcelFile

    async def callback(response, _):
        """Read the response and return the ExcelFile object."""
        res = await response.read()
        file = ExcelFile(BytesIO(res))
        return file

    # Clear the cache to download the file again.
    if use_cache is False:
        download_excel_file.cache_invalidate(url)

    try:
        return await amake_request(url, response_callback=callback)
    except Exception as e:  # pylint: disable=broad-except
        raise OpenBBError(f"Error downloading the file from the EIA site -> {e}") from e
