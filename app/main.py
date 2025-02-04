# import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from app.auth import auth_routes
from app.events import events_routes
from fastapi.middleware.gzip import GZipMiddleware
import arel
from fastapi.staticfiles import StaticFiles
from app.core import settings, templates
from app.core.deps import IsUserAuthenticatedDeps
from starlette.middleware.cors import CORSMiddleware

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

application.mount("/static", StaticFiles(directory="static"), name="static")

# to serve compressed files
application.add_middleware(GZipMiddleware)

# Include routers
application.include_router(auth_routes.router)
application.include_router(events_routes.router)


@application.get("/", name="homepage")
def get_homepage(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="homepage.html")


@application.get("/authentication", name="auth")
def get_authentication_page(
    request: Request, redirect_url: IsUserAuthenticatedDeps
) -> HTMLResponse:
    if isinstance(redirect_url, RedirectResponse):
        return redirect_url
    return templates.TemplateResponse(request=request, name="authentication.html")


# use `python -m app.main` to run this in base python
# if __name__ == "__main__":
#     uvicorn.run(
#         "app.main:application",
#         host="127.0.0.1",
#         port=5000,
#         reload=True if settings.DEBUG else False,
#     )

# TODO: catch error
# bson.errors.InvalidId
# HTTPMessageException
