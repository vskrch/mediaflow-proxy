from typing import Iterable
import pytest
from starlette.datastructures import URL

from mediaflow_proxy.utils.m3u8_processor import M3U8Processor


class DummyRequest:
    def __init__(self):
        self.headers = {}
        self.query_params = {}
        self.url = URL("http://testserver")

    def url_for(self, name: str) -> URL:
        return URL(f"http://testserver/{name}")


class SimpleProcessor(M3U8Processor):
    async def process_key_line(self, line: str, base_url: str) -> str:  # type: ignore[override]
        return line

    async def proxy_content_url(self, url: str, base_url: str) -> str:  # type: ignore[override]
        return url

    async def proxy_url(self, url: str, base_url: str, use_full_url: bool = False) -> str:  # type: ignore[override]
        return url


class FailingString(str):
    def splitlines(self):  # pragma: no cover - used to ensure it is not called
        raise AssertionError("splitlines should not be used")


@pytest.mark.asyncio
async def test_process_m3u8_iterable():
    req = DummyRequest()
    processor = SimpleProcessor(req)

    def gen() -> Iterable[str]:
        for i in range(1000):
            yield f"http://example.com/seg{i}.ts"

    result = await processor.process_m3u8(gen(), "http://base/")
    lines = result.splitlines()
    assert lines[0] == "http://example.com/seg0.ts"
    assert lines[-1] == "http://example.com/seg999.ts"
    assert len(lines) == 1000


@pytest.mark.asyncio
async def test_process_m3u8_large_string_no_splitlines():
    req = DummyRequest()
    processor = SimpleProcessor(req)
    content = FailingString("\n".join(f"line{i}" for i in range(2000)))

    result = await processor.process_m3u8(content, "http://base/")
    lines = result.splitlines()
    assert lines[0] == "line0"
    assert lines[-1] == "line1999"
    assert len(lines) == 2000
