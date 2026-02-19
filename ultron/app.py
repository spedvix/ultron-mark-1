from __future__ import annotations

from fastapi import FastAPI

from .settings import settings
from .utils.logging import configure_logging, get_logger


def create_app() -> FastAPI:
    """Application factory for Ultron backend."""
    configure_logging(settings.log_level, settings.mask_pii)
    app = FastAPI(
        title="Ultron Academic Assistant",
        version="0.1.0",
        description="Aggregates academic data sources and surfaces actionable insights.",
    )

    logger = get_logger(__name__)
    logger.debug("Initializing FastAPI app with timezone %s", settings.timezone)

    from .api import routes_brief, routes_calendar, routes_status, routes_deadlines, routes_gpa, routes_chat

    app.include_router(routes_status.router, prefix="/status", tags=["status"])
    app.include_router(routes_brief.router, prefix="/brief", tags=["brief"])
    app.include_router(routes_calendar.router, prefix="/schedule", tags=["schedule"])
    app.include_router(routes_deadlines.router, prefix="/deadlines", tags=["deadlines"])
    app.include_router(routes_calendar.ics_router, prefix="/ics", tags=["calendar"])
    app.include_router(routes_gpa.router, prefix="/gpa", tags=["gpa"])
    app.include_router(routes_chat.router, prefix="/api", tags=["chat"])

    return app


app = create_app()
