"""Entry point launching the Soundboard Design web interface."""

import argparse

import uvicorn

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000


def parse_arguments() -> argparse.Namespace:
    """Parse the command line arguments controlling the server.

    Returns:
        The parsed arguments, holding host, port and reload settings.
    """
    parser = argparse.ArgumentParser(
        description="Lance l'interface web Soundboard Design.",
    )
    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help=f"Adresse d'écoute (par défaut {DEFAULT_HOST}).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Port d'écoute (par défaut {DEFAULT_PORT}).",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Recharge le serveur à chaque modification du code.",
    )
    return parser.parse_args()


def main() -> None:
    """Start the development server with the parsed command line options."""
    arguments = parse_arguments()

    uvicorn.run(
        "soundboard_design.server:app",
        host=arguments.host,
        port=arguments.port,
        reload=arguments.reload,
    )


if __name__ == "__main__":
    main()
