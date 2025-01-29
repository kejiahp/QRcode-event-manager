from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.core import templates

router = APIRouter(prefix="/user")


@router.get("/login", response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse(
        request=request, name="homepage.html", context={"id": id}
    )
