import pytest
from urllib import parse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mediaflow_proxy.utils.http_utils import (
    encode_mediaflow_proxy_url,
    encode_stremio_proxy_url,
)
from mediaflow_proxy.utils.crypto_utils import EncryptionHandler


@pytest.fixture
def request_headers():
    return {"User-Agent": "TestAgent", "Accept": "video/mp4"}


@pytest.fixture
def response_headers():
    return {"Cache-Control": "no-cache"}


@pytest.fixture
def destination_url():
    return "http://example.com/video.mp4?foo=bar"


@pytest.fixture
def encryption_handler():
    return EncryptionHandler("secret-key-123456")


def test_mediaflow_header_encoding(request_headers, response_headers, destination_url):
    url = encode_mediaflow_proxy_url(
        "http://proxy.local",
        "stream",
        destination_url,
        request_headers=request_headers,
        response_headers=response_headers,
    )
    parsed = parse.urlparse(url)
    qs = parse.parse_qs(parsed.query)
    assert qs["d"] == [destination_url]
    assert qs["h_User-Agent"] == ["TestAgent"]
    assert qs["h_Accept"] == ["video/mp4"]
    assert qs["r_Cache-Control"] == ["no-cache"]
    assert parsed.path == "/stream"


def test_mediaflow_filename_without_encryption(destination_url):
    url = encode_mediaflow_proxy_url(
        "http://proxy.local/",
        "stream",
        destination_url,
        filename="my file.ts",
    )
    parsed = parse.urlparse(url)
    assert parsed.path == "/stream/my%20file.ts"
    assert "d=" in parsed.query


def test_mediaflow_encryption_token_placement(request_headers, response_headers, destination_url, encryption_handler):
    url = encode_mediaflow_proxy_url(
        "http://proxy.local",
        "stream",
        destination_url,
        request_headers=request_headers,
        response_headers=response_headers,
        encryption_handler=encryption_handler,
        filename="video.ts",
    )
    parsed = parse.urlparse(url)
    assert parsed.query == ""
    segments = parsed.path.split("/")
    assert segments[1].startswith("_token_")
    token = segments[1][len("_token_") :]
    decrypted = encryption_handler.decrypt_data(token, "127.0.0.1")
    expected = {
        "d": destination_url,
        "h_User-Agent": "TestAgent",
        "h_Accept": "video/mp4",
        "r_Cache-Control": "no-cache",
    }
    assert decrypted == expected
    assert segments[2] == "stream"
    assert segments[3] == "video.ts"


def test_stremio_header_encoding(request_headers, response_headers, destination_url):
    url = encode_stremio_proxy_url(
        "http://127.0.0.1:11470",
        destination_url,
        request_headers=request_headers,
        response_headers=response_headers,
    )
    parsed = parse.urlparse(url)
    assert parsed.path.startswith("/proxy/")
    segments = parsed.path.split("/")
    query_part = segments[2]
    qs = parse.parse_qs(query_part)
    assert qs["d"] == ["http://example.com"]
    assert set(qs["h"]) == {"User-Agent:TestAgent", "Accept:video/mp4"}
    assert qs["r"] == ["Cache-Control:no-cache"]
    assert segments[3] == "video.mp4"
    assert parsed.query == "foo=bar"


def test_stremio_filename_and_no_token(destination_url):
    url = encode_stremio_proxy_url("http://127.0.0.1:11470/", destination_url)
    parsed = parse.urlparse(url)
    assert parsed.path.split("/")[3] == "video.mp4"
    assert "_token_" not in parsed.path
