"""Documents handed to the Workspace file viewer."""

PDF_MAGIC = b"%PDF"


async def _download(url: str) -> bytes | None:
    """Read one document, or nothing when the host will not serve it."""
    from openbb_tmx.utils.cache import amake_request

    try:
        body = await amake_request(
            url, use_cache=False, accept_type="binary", referer=url
        )
    except Exception:  # noqa: BLE001
        return None

    return body if isinstance(body, bytes) and body.startswith(PDF_MAGIC) else None


async def as_viewer_files(selections: "list[tuple[str, str]]") -> list[dict]:
    """Serve each selected document to the file viewer.

    Parameters
    ----------
    selections : list[tuple[str, str]]
        The URL and the file name of each selected document.

    Returns
    -------
    list[dict]
        One entry per document, carrying the document itself where the host
        served it and the URL to load where it did not.
    """
    import asyncio
    from base64 import b64encode

    documents = await asyncio.gather(*(_download(url) for url, _ in selections))
    results: list[dict] = []

    for (url, filename), document in zip(selections, documents):
        entry: dict = {"data_format": {"data_type": "pdf", "filename": filename}}

        if document is None:
            entry["url"] = url
        else:
            entry["content"] = b64encode(document).decode("utf-8")

        results.append(entry)

    return results
