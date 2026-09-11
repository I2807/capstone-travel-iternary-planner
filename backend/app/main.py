from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import Settings, get_settings
from app.errors import AppError, create_request_id, safe_error_message
from app.logging import configure_logging, get_logger
from app.routers.chat import router as chat_router
from app.routers.health import router as health_router
from app.schemas.responses import ErrorEnvelope

logger = get_logger(__name__)


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", None) or create_request_id()


def _error_response(request: Request, error: AppError) -> JSONResponse:
    request_id = error.request_id or _request_id(request)
    payload = ErrorEnvelope(
        error={"code": error.code, "message": error.message},
        request_id=request_id,
    ).model_dump(mode="json")
    return JSONResponse(
        status_code=error.status_code,
        content=payload,
        headers={"X-Request-ID": request_id},
    )


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    configure_logging(app_settings.log_level)
    app = FastAPI(title="Voyager AI Travel Planner", version="0.1.0")
    app.state.settings = app_settings

    if settings is not None:
        app.dependency_overrides[get_settings] = lambda: app_settings

    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.cors_origin_list,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
    )

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or create_request_id()
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        return _error_response(request, exc)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        del exc
        return _error_response(
            request,
            AppError.create(
                "INVALID_REQUEST",
                safe_error_message("INVALID_REQUEST"),
            ),
        )

    @app.exception_handler(HTTPException)
    async def http_error_handler(request: Request, exc: HTTPException) -> JSONResponse:
        error = AppError.create(
            "INVALID_REQUEST",
            (
                str(exc.detail)
                if isinstance(exc.detail, str)
                else safe_error_message("INVALID_REQUEST")
            ),
        )
        error.status_code = exc.status_code
        return _error_response(request, error)

    @app.exception_handler(Exception)
    async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
        del exc
        request_id = _request_id(request)
        logger.exception("unhandled_error request_id=%s path=%s", request_id, request.url.path)
        return _error_response(
            request,
            AppError.create(
                "INTERNAL_ERROR",
                safe_error_message("INTERNAL_ERROR"),
                request_id,
            ),
        )

    app.include_router(health_router)
    app.include_router(chat_router)

    frontend_directory = Path(__file__).resolve().parents[2] / "frontend" / "dist"
    if frontend_directory.is_dir():
        app.frontend("/", directory=str(frontend_directory))

    return app


app = create_app()
