"""Tests for the documents handed to the file viewer."""

from base64 import b64decode

import pytest

from openbb_tmx.utils.documents import as_viewer_files

PDF = b"%PDF-1.6 document bytes"


@pytest.fixture
def host(monkeypatch):
    """Answer each download from a scripted table."""
    answers: dict = {}

    async def download(url, use_cache=True, accept_type="json", **kwargs):
        answer = answers[url]

        if isinstance(answer, Exception):
            raise answer

        return answer

    monkeypatch.setattr("openbb_tmx.utils.cache.amake_request", download)

    return answers


class TestViewerFiles:
    """A document is served whole where the host allows it."""

    async def test_a_served_document_is_handed_over_whole(self, host):
        host["https://host/a.pdf"] = PDF
        files = await as_viewer_files([("https://host/a.pdf", "A.pdf")])

        assert b64decode(files[0]["content"]) == PDF
        assert files[0]["data_format"] == {"data_type": "pdf", "filename": "A.pdf"}
        assert "url" not in files[0]

    async def test_a_refused_document_falls_back_to_its_url(self, host):
        host["https://host/a.pdf"] = OSError("forbidden")
        files = await as_viewer_files([("https://host/a.pdf", "A.pdf")])

        assert files[0]["url"] == "https://host/a.pdf"
        assert "content" not in files[0]

    async def test_a_page_served_instead_of_a_document_falls_back(self, host):
        host["https://host/a.pdf"] = b"<HTML>Forbidden</HTML>"
        files = await as_viewer_files([("https://host/a.pdf", "A.pdf")])

        assert files[0]["url"] == "https://host/a.pdf"

    async def test_an_empty_answer_falls_back(self, host):
        host["https://host/a.pdf"] = None
        files = await as_viewer_files([("https://host/a.pdf", "A.pdf")])

        assert files[0]["url"] == "https://host/a.pdf"

    async def test_every_selection_is_served(self, host):
        host["https://host/a.pdf"] = PDF
        host["https://host/b.pdf"] = OSError("forbidden")
        files = await as_viewer_files(
            [("https://host/a.pdf", "A.pdf"), ("https://host/b.pdf", "B.pdf")]
        )

        assert [f["data_format"]["filename"] for f in files] == ["A.pdf", "B.pdf"]
        assert "content" in files[0]
        assert "url" in files[1]

    async def test_nothing_selected_is_nothing_served(self):
        assert await as_viewer_files([]) == []
