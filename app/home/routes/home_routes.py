from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.core import templates

# router = APIRouter(prefix="home")
router = APIRouter()


@router.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse(
        request=request, name="homepage.html", context={"id": id}
    )
