from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core import exceptions
from app.infraestructure.db.config import init_db
from app.infraestructure.security.config import init_security


def create_app() -> FastAPI:
    """Create the application."""
    app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix=settings.API_V1_STR)
    return app


app = create_app()


@app.on_event("startup")
def startup_event():
    """Event start up"""
    init_db()
    init_security()


@app.exception_handler(exceptions.ORMError)
def orm_error_hanlder(request, exc: exceptions.ORMError):
    exc_message = str(exc)
    content = {"detail": f"ORM Error: {exc_message}"}
    if "violates unique constraint" in exc_message:
        message = (
            exc_message.split(":")[1]
            .replace("(", "")
            .replace(")", "")
            .replace("Key", "")
            .replace("=", " ")
            .strip()
            .capitalize()
        )
        content = {"detail": f"{message} please try with another one."}
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=content,
    )


@app.exception_handler(exceptions.NoObserverRegister)
def no_observer_register_handler(request, exc: exceptions.NoObserverRegister):
    return JSONResponse(
        content={"detail": f"Service unavailable {exc.service}"},
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    )


@app.exception_handler(exceptions.InvalidCredentials)
def invalid_credentials_handler(request, exc: exceptions.InvalidCredentials):
    return JSONResponse(
        content={"detail": f"Invalid credentials {exc.msg}"},
        status_code=status.HTTP_403_FORBIDDEN,
    )
