# from typing import Union

from fastapi import FastAPI
from app.home.routes import home_routes

app = FastAPI()

# from fastapi.staticfiles import StaticFiles
# app.mount("/static", StaticFiles(directory="static"), name="static")


# Include routers
app.include_router(home_routes.router)


@app.get("/")
def read_root():
    return {"Hello": "World"}


# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}
