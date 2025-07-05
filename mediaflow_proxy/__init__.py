# Read version from pyproject.toml and expose key modules
from __future__ import annotations

from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover - fall back for older versions
    import tomli as tomllib  # type: ignore


def _load_version() -> str:
    project_root = Path(__file__).resolve().parent.parent
    pyproject_file = project_root / "pyproject.toml"
    if pyproject_file.is_file():
        with pyproject_file.open("rb") as f:
            data = tomllib.load(f)
        return data["tool"]["poetry"]["version"]
    return "0.0.0"


__version__ = _load_version()


# Export major modules for easier access
from . import (
    configs,
    const,
    drm,
    extractors,
    handlers,
    main,
    middleware,
    mpd_processor,
    routes,
    schemas,
    speedtest,
    utils,
)

__all__ = [
    "__version__",
    "configs",
    "const",
    "drm",
    "extractors",
    "handlers",
    "main",
    "middleware",
    "mpd_processor",
    "routes",
    "schemas",
    "speedtest",
    "utils",
]
