from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from app.home import home_routes
from app.user import user_routes
from fastapi.middleware.gzip import GZipMiddleware
import arel
from fastapi.staticfiles import StaticFiles
from app.core import settings, templates

app = FastAPI()


async def reload_logger():
    print("Arel triggered server reload...")


if _debug := settings.DEBUG:
    # tracks all files in directory for changes
    hot_reload = arel.HotReload(paths=[arel.Path(".", on_reload=[reload_logger])])
    app.add_websocket_route("/hot-reload", route=hot_reload, name="hot-reload")
    app.add_event_handler("startup", hot_reload.startup)
    app.add_event_handler("shutdown", hot_reload.shutdown)

    templates.env.globals["DEBUG"] = _debug
    templates.env.globals["hot_reload"] = hot_reload

app.mount("/static", StaticFiles(directory="static"), name="static")

# to serve compressed files
app.add_middleware(GZipMiddleware)

# Include routers
app.include_router(home_routes.router)
app.include_router(user_routes.router)


@app.get("/", name="homepage")
def get_homepage(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="homepage.html")


@app.get("/authentication", name="auth")
def get_authentication_page(
    request: Request,
) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="authentication.html")
