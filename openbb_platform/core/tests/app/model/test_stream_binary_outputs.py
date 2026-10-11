"""Public stream output accepts binary files as well as text sinks."""

from io import BytesIO, StringIO

from openbb_core.app.model.stream import OBBStream


async def chunks():
    for chunk in ["héllo\n", b"raw\xff\n", {"value": 1}]:
        yield chunk


def test_binary_memory_output_preserves_raw_bytes():
    sink = BytesIO()
    stream = OBBStream(chunks()).start(output=sink)
    stream.wait(timeout=5)
    assert not stream.running
    assert sink.getvalue() == b'h\xc3\xa9llo\nraw\xff\n{"value": 1}\n'
    assert not sink.closed


def test_binary_disk_output(tmp_path):
    path = tmp_path / "stream.bin"
    with path.open("wb") as sink:
        stream = OBBStream(chunks()).start(output=sink)
        stream.wait(timeout=5)
        assert not stream.running
        assert not sink.closed
    assert path.read_bytes() == b'h\xc3\xa9llo\nraw\xff\n{"value": 1}\n'


def test_text_output_keeps_existing_decoding():
    sink = StringIO()
    stream = OBBStream(chunks()).start(output=sink)
    stream.wait(timeout=5)
    assert sink.getvalue() == 'héllo\nraw\ufffd\n{"value": 1}\n'
