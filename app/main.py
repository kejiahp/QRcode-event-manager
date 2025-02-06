# import uvicorn
import arel
from bson.errors import BSONError
from fastapi import FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
    JSONResponse,
)
from starlette.middleware.cors import CORSMiddleware
from pathlib import Path

from app.auth import auth_routes
from app.events import events_routes
from app.core import settings, templates
from app.core.deps import IsUserAuthenticatedDeps
from app.core.utils import HTTPMessageException, STATUS_CODE_TO_MESSAGE

application = FastAPI()


async def reload_logger():
    print("Arel triggered server reload...")


# Set all CORS enabled origins
if settings.all_cors_origins:
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# reload frontend on file change
if _debug := settings.DEBUG:
    # tracks all files in directory for changes
    hot_reload = arel.HotReload(paths=[arel.Path(".", on_reload=[reload_logger])])
    application.add_websocket_route("/hot-reload", route=hot_reload, name="hot-reload")
    application.add_event_handler("startup", hot_reload.startup)
    application.add_event_handler("shutdown", hot_reload.shutdown)

    templates.env.globals["DEBUG"] = _debug
    templates.env.globals["hot_reload"] = hot_reload


@application.middleware("http")
async def force_https_middleware(request: Request, call_next):
    """
    Railways load balancer seem to be converting the `scheme` header from `https` to `http` making urls built using `request.url_for` have the `http` protocol in prodution rather than `https`.

    Hence, I decided to force `https` protocol in production servers, using the `X-Forwarded-Proto` header added to requests by the load balancer or proxy (I dunno the specifics 🤷‍♂️)
    """
    if settings.ENVIRONMENT == "production":
        if (lb_proto := request.headers.get("X-Forwarded-Proto", "http")) == "https":
            request.scope["scheme"] = "https"  # Force HTTPS
    return await call_next(request)


static_dir = Path(__file__).parent.parent / "static"
static_dir = str(static_dir)

application.mount("/static", StaticFiles(directory=static_dir), name="static")

# to serve compressed files
application.add_middleware(GZipMiddleware)

# Include routers
application.include_router(auth_routes.router)
application.include_router(events_routes.router)


@application.get("/", name="homepage")
def get_homepage(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="homepage.html")


@application.get("/forgot-password", name="forgot_password")
def forgot_password_page(
    request: Request, email: str = None, reset_code: str = None
) -> HTMLResponse:
    context = {"reset_code": reset_code, "email": email}
    return templates.TemplateResponse(
        request=request, name="forgot_password.html", context=context
    )


@application.get("/authentication", name="auth")
def get_authentication_page(
    request: Request, redirect_url: IsUserAuthenticatedDeps
) -> HTMLResponse:
    if isinstance(redirect_url, RedirectResponse):
        return redirect_url
    return templates.TemplateResponse(request=request, name="authentication.html")


# @application.get("/debug")
# def debug_headers(request: Request):
#     """
#     view all headers set by the load balancer or proxy before sending the request to the running server hosted on Railway
#     """
#     all_headers = {k: v for k, v in request.headers.items()}
#     return {
#         "X-Forwarded-Proto": request.headers.get("X-Forwarded-Proto", "MISSING"),
#         ":scheme:": request.headers.get("scheme:", "MISSING"),
#         "scheme": request.url.scheme,
#         "all_headers": all_headers,
#     }


@application.exception_handler(HTTPMessageException)
def http_msg_exception_handler(request: Request, exc: HTTPMessageException):
    if exc.json_res:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    title = STATUS_CODE_TO_MESSAGE.get(exc.status_code, None)
    context = {
        "title": title,
        "message": exc.detail["message"],
        "status_code": exc.detail["status_code"],
    }
    return templates.TemplateResponse(
        request=request, name="error_page.html", context=context
    )


@application.exception_handler(BSONError)
def invalid_objectID_exception_handler(request: Request, exc: BSONError):
    if len(exc.args) > 0 and isinstance(exc.args[0], str):
        msg = exc.args[0]
    return templates.TemplateResponse(
        request=request,
        name="error_page.html",
        context={"message": msg, "status_code": 500},
    )


# use `python -m app.main` to run this in base python
# if __name__ == "__main__":
#     uvicorn.run(
#         "app.main:application",
#         host="127.0.0.1",
#         port=5000,
#         reload=True if settings.DEBUG else False,
#     )
