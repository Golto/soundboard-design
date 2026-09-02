"""HTTP server exposing the design system and the web interface.

The synthesis itself runs in the browser, where the Web Audio API can
schedule notes with sample accuracy and render offline exports. The server
only owns the definitions and serves the static interface.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .design_system import build_design_system_payload, count_tokens
from .domain import JsonValue

STATIC_DIRECTORY = Path(__file__).parent / "static"


def create_app() -> FastAPI:
    """Build the FastAPI application serving the interface and the payload.

    The design system is assembled and validated once at startup so that an
    inconsistent definition fails immediately instead of reaching the
    browser.

    Returns:
        A configured FastAPI application.

    Raises:
        ValueError: If the design system definitions are inconsistent.
        FileNotFoundError: If the static directory is missing.
    """
    if not STATIC_DIRECTORY.is_dir():
        raise FileNotFoundError(f"Static directory not found: {STATIC_DIRECTORY}")

    payload = build_design_system_payload()
    token_count = count_tokens()

    app = FastAPI(
        title="Soundboard Design",
        description="Palettes sonores cohérentes pour systèmes de design",
        version=str(payload["version"]),
    )

    @app.get("/api/design-system")
    def read_design_system() -> dict[str, JsonValue]:
        """Return the full design system consumed by the browser engine."""
        return payload

    @app.get("/api/health")
    def read_health() -> dict[str, JsonValue]:
        """Return a short status summary useful for smoke testing."""
        return {
            "status": "ok",
            "version": payload["version"],
            "tokenCount": token_count,
        }

    @app.get("/")
    def read_index() -> FileResponse:
        """Serve the single page interface."""
        return FileResponse(STATIC_DIRECTORY / "index.html")

    app.mount("/static", StaticFiles(directory=STATIC_DIRECTORY), name="static")

    return app


app = create_app()
