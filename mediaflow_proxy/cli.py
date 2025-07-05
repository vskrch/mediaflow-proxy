import json
from pathlib import Path
from typing import Optional

import typer

from mediaflow_proxy.utils.crypto_utils import EncryptionHandler
from mediaflow_proxy.utils.http_utils import encode_mediaflow_proxy_url

app = typer.Typer(help="Utilities for generating MediaFlow Proxy URLs")


def _load_json(value: Optional[str]) -> dict:
    if not value:
        return {}
    try:
        return json.loads(value)
    except json.JSONDecodeError as e:
        raise typer.BadParameter(f"Invalid JSON: {e}")


@app.command()
def generate_url(
    mediaflow_proxy_url: str = typer.Option(..., help="Base MediaFlow Proxy URL"),
    endpoint: Optional[str] = typer.Option(None, help="Proxy endpoint"),
    destination_url: Optional[str] = typer.Option(None, help="Destination URL"),
    query_params: Optional[str] = typer.Option(None, help="JSON string of query parameters"),
    request_headers: Optional[str] = typer.Option(None, help="JSON string of request headers"),
    response_headers: Optional[str] = typer.Option(None, help="JSON string of response headers"),
    expiration: Optional[int] = typer.Option(None, help="Token expiration in seconds"),
    api_password: Optional[str] = typer.Option(None, help="Password for encryption"),
    ip: Optional[str] = typer.Option(None, help="Restrict URL to this IP"),
    filename: Optional[str] = typer.Option(None, help="Preserved filename"),
):
    """Generate a single encoded or encrypted URL."""
    query_dict = _load_json(query_params)
    request_headers_dict = _load_json(request_headers)
    response_headers_dict = _load_json(response_headers)

    if api_password and "api_password" not in query_dict:
        query_dict["api_password"] = api_password

    handler = EncryptionHandler(api_password) if api_password else None
    url = encode_mediaflow_proxy_url(
        mediaflow_proxy_url=mediaflow_proxy_url,
        endpoint=endpoint,
        destination_url=destination_url,
        query_params=query_dict,
        request_headers=request_headers_dict,
        response_headers=response_headers_dict,
        encryption_handler=handler,
        expiration=expiration,
        ip=ip,
        filename=filename,
    )
    typer.echo(url)


@app.command()
def generate_urls(
    urls_file: Path = typer.Argument(..., exists=True, readable=True, help="Path to JSON file with URL items"),
    mediaflow_proxy_url: str = typer.Option(..., help="Base MediaFlow Proxy URL"),
    api_password: Optional[str] = typer.Option(None, help="Password for encryption"),
    expiration: Optional[int] = typer.Option(None, help="Token expiration in seconds"),
    ip: Optional[str] = typer.Option(None, help="Restrict URLs to this IP"),
):
    """Generate multiple encoded or encrypted URLs from a JSON file."""
    data = json.loads(urls_file.read_text())
    handler = EncryptionHandler(api_password) if api_password else None
    encoded_urls = []
    for item in data:
        query_dict = item.get("query_params", {})
        if api_password and "api_password" not in query_dict:
            query_dict["api_password"] = api_password
        encoded_urls.append(
            encode_mediaflow_proxy_url(
                mediaflow_proxy_url=mediaflow_proxy_url,
                endpoint=item.get("endpoint"),
                destination_url=item.get("destination_url"),
                query_params=query_dict,
                request_headers=item.get("request_headers", {}),
                response_headers=item.get("response_headers", {}),
                encryption_handler=handler,
                expiration=expiration,
                ip=ip,
                filename=item.get("filename"),
            )
        )
    typer.echo(json.dumps({"urls": encoded_urls}, indent=2))


if __name__ == "__main__":
    app()
