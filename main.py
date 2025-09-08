from typing import Optional

import uvicorn

from config.config import app_settings


def run(
    host: Optional[str] = None,
    port: Optional[int] = None,
) -> None:
    """
    Run the server.
    """
    if not host:
        host = app_settings.APP_HOST
    if not port:
        port = app_settings.APP_PORT

    uvicorn.run(
        "server:debug_app",
        host=host,
        port=port,
        reload=True,
        reload_dirs=["."],
        log_level="debug",
        use_colors=True,
    )


if __name__ == "__main__":
    run()
