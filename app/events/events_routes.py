from fastapi import APIRouter, Request, Cookie
from fastapi.responses import HTMLResponse
from app.core import settings, templates
from typing import Annotated, Union

router = APIRouter(prefix="/events")


@router.get("/", name="events")
def get_events_page(
    request: Request, tk: Annotated[Union[str, None], Cookie()] = None
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request, name="events_page.html", context={"token": tk}
    )
