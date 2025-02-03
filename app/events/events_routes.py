from bson import ObjectId
from fastapi import APIRouter, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Annotated

from .events_models import (
    CreateEventModel,
    EventModel,
    EventCollection,
    InviteModel,
    CreateInviteModel,
)
from app.core import settings, templates
from app.core import get_collection, MONGO_COLLECTIONS
from app.core.deps import CurrentUserDeps
from app.core.utils import HTTPMessageException, collection_error_msg

router = APIRouter(prefix="/events")


@router.get("/", name="events")
def get_events_page(request: Request, current_user: CurrentUserDeps) -> HTMLResponse:
    event_collection = get_collection(MONGO_COLLECTIONS.EVENTS)
    if event_collection is None:
        raise HTTPMessageException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=collection_error_msg("create_event", MONGO_COLLECTIONS.EVENTS.name),
            success=False,
        )

    events = event_collection.find({"created_by": current_user.id}).to_list(1000)
    events_list = EventCollection(events=events).model_dump()

    context = {"email": current_user.email, "events": events_list["events"]}

    return templates.TemplateResponse(
        request=request, name="events_page.html", context=context
    )


@router.get("/{event_id}", name="single_event")
def get_single_event(
    request: Request, event_id: str, current_user: CurrentUserDeps
) -> HTMLResponse:
    event_collection = get_collection(MONGO_COLLECTIONS.EVENTS)
    if event_collection is None:
        raise HTTPMessageException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=collection_error_msg("create_event", MONGO_COLLECTIONS.EVENTS.name),
            success=False,
        )
    event = event_collection.find_one(
        {"_id": ObjectId(event_id), "created_by": current_user.id}
    )
    event = EventModel(**event).model_dump()
    context = {"event": event}
    return templates.TemplateResponse(
        request=request, name="event_details_page.html", context=context
    )


@router.post("/create", name="create_event")
def create_event(
    request: Request,
    event_dto: Annotated[CreateEventModel, Form()],
    current_user: CurrentUserDeps,
):
    event_collection = get_collection(MONGO_COLLECTIONS.EVENTS)
    if event_collection is None:
        raise HTTPMessageException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=collection_error_msg("create_event", MONGO_COLLECTIONS.EVENTS.name),
            success=False,
        )

    event_dto = event_dto.model_dump()
    event_dto["created_by"] = current_user.id
    event = EventModel(**event_dto)

    # create a new event
    event_collection.insert_one(event.model_dump(by_alias=True, exclude=["id"]))

    return RedirectResponse(
        url=request.url_for("events"), status_code=status.HTTP_302_FOUND
    )


@router.post("/create-invitation/{event_id}", name="create_invitation")
def create_invitation(
    request: Request,
    event_id: str,
    invite_dto: Annotated[CreateInviteModel, Form()],
    current_user: CurrentUserDeps,
):
    event_collection = get_collection(MONGO_COLLECTIONS.EVENTS)
    if event_collection is None:
        raise HTTPMessageException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=collection_error_msg("create_event", MONGO_COLLECTIONS.EVENTS.name),
            success=False,
        )
    if (event := event_collection.find_one({"_id": event_id})) is None:
        raise HTTPMessageException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"event with id '{event_id}' does not exist",
            success=False,
        )
    print(invite_dto.model_dump())
    # current_user
    # print(InviteModel(**invite_dto.model_dump()))

    return RedirectResponse(
        url=request.url_for("single_event"), status_code=status.HTTP_302_FOUND
    )
