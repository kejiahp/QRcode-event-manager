from bson import ObjectId
from datetime import datetime
from fastapi import APIRouter, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Annotated
from secrets import token_urlsafe
import urllib.parse

from pymongo import ReturnDocument

from .events_models import (
    CreateEventModel,
    EventModel,
    EventCollection,
    InviteModel,
    CreateInviteModel,
    InviteCollection,
)
from app.core import templates
from app.core import get_collection, MONGO_COLLECTIONS
from app.core.deps import CurrentUserDeps
from app.core.utils import HTTPMessageException, collection_error_msg
from app.core.cloudinary_uploader import create_n_upload_qrcode
from app.core.mailing import generate_event_invitation_email, send_email

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
) -> RedirectResponse:
    event_collection = get_collection(MONGO_COLLECTIONS.EVENTS)
    if event_collection is None:
        raise HTTPMessageException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=collection_error_msg(
                "create_invitation", MONGO_COLLECTIONS.EVENTS.name
            ),
            success=False,
        )

    invite_collection = get_collection(MONGO_COLLECTIONS.INVITE)
    if invite_collection is None:
        raise HTTPMessageException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=collection_error_msg(
                "create_invitation", MONGO_COLLECTIONS.INVITE.name
            ),
            success=False,
        )

    if (
        event := event_collection.find_one(
            {"_id": ObjectId(event_id), "created_by": current_user.id}
        )
    ) is None:
        raise HTTPMessageException(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"event does not exist",
            success=False,
        )
    event = EventModel(**event)

    if (
        invite_exist := invite_collection.find_one(
            {"email": invite_dto.email, "event_invited_to": event_id}
        )
    ) is not None:
        raise HTTPMessageException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=f"guest with email '{invite_dto.email}' has already been invited to this event",
        )

    rand_code = f"INVITE_{token_urlsafe(8)}"
    code_url = request.url_for("verify_invite_code", invite_code=rand_code)
    try:
        cloudinary_res = create_n_upload_qrcode(code_url)
    except Exception as exception:
        print(exception)
        raise HTTPMessageException(
            message=(
                exception.message
                if hasattr(exception, "message")
                else "Something went wrong"
            ),
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            success=False,
        )

    invite = InviteModel(
        email=invite_dto.email,
        fullname=invite_dto.fullname,
        event_invited_to=event_id,
        code=rand_code,
        qr_code_img_url=cloudinary_res.secure_url,
        qr_code_img_public_key=cloudinary_res.public_id,
        created_by=current_user.id,
    )

    invite_collection.insert_one(invite.model_dump(by_alias=True, exclude=["id"]))
    # new_invite = invite_collection.find_one({"_id": inserted_invite.inserted_id})

    try:
        email_data = generate_event_invitation_email(
            fullname=invite.fullname,
            qrcode_img_url=invite.qr_code_img_url,
            event_name=event.name,
            org_name="Organiser",
            org_contact=current_user.email,
        )

        send_email(
            email_to=invite.email,
            html_content=email_data.html_content,
            subject=email_data.subject,
        )
    except Exception as exc:
        print("#### FAILED TO SEND GUEST INVITATION EMAIL ####")
        print(exc)
        print("#### FAILED TO SEND GUEST INVITATION EMAIL ####")

        raise HTTPMessageException(
            message=(
                exc.message if hasattr(exc, "message") else "Something went wrong"
            ),
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            success=False,
        )

    return RedirectResponse(
        url=request.url_for("single_event", event_id=event_id),
        status_code=status.HTTP_302_FOUND,
    )


@router.get("/invite/{invite_id}", name="single_invite")
def single_invite_page(request: Request, invite_id: str, current_user: CurrentUserDeps):
    invite_collection = get_collection(MONGO_COLLECTIONS.INVITE)
    if invite_collection is None:
        raise HTTPMessageException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=collection_error_msg(
                "create_invitation", MONGO_COLLECTIONS.INVITE.name
            ),
            success=False,
        )
    if (
        invite := invite_collection.find_one(
            {"_id": ObjectId(invite_id), "created_by": current_user.id}
        )
    ) is None:
        raise HTTPMessageException(
            status_code=status.HTTP_404_NOT_FOUND, message="invite does not exist"
        )
    invite = InviteModel(**invite)
    context = {"invite": invite.model_dump()}
    return templates.TemplateResponse(
        request=request, name="invite_details_page.html", context=context
    )


@router.get("/verify-invite/{invite_code}", name="verify_invite_code")
def verify_invite_code(
    request: Request, invite_code: str, current_user: CurrentUserDeps
):
    invite_collection = get_collection(MONGO_COLLECTIONS.INVITE)
    if invite_collection is None:
        raise HTTPMessageException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=collection_error_msg(
                "create_invitation", MONGO_COLLECTIONS.INVITE.name
            ),
            success=False,
        )

    if (
        invite := invite_collection.find_one(
            {"code": invite_code, "created_by": current_user.id}
        )
    ) is None:
        raise HTTPMessageException(
            status_code=status.HTTP_404_NOT_FOUND, message="invite does not exist"
        )
    invite = InviteModel(**invite)

    if invite.invite_accepted or invite.invite_accepted_at is not None:
        raise HTTPMessageException(
            message="Invitation already accepted",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    update_opt = {"invite_accepted": True, "invite_accepted_at": datetime.now()}

    update_result = invite_collection.find_one_and_update(
        {"_id": ObjectId(invite.id)},
        {"$set": update_opt},
        return_document=ReturnDocument.AFTER,
    )
    if update_result is not None:
        query_string = urllib.parse.urlencode(
            {"message": f"{invite.fullname}'s invite is valid"}
        )
        return RedirectResponse(
            status_code=status.HTTP_302_FOUND,
            url=f"{request.url_for("verification_result")}?{query_string}",
        )
    else:
        raise HTTPMessageException(
            status_code=status.HTTP_404_NOT_FOUND, details="invite does not exist"
        )


@router.get("/verification-result", name="verification_result")
def verification_result_page(
    request: Request,
    current_user: CurrentUserDeps,
    message: str = None,
):
    if message is None:
        raise HTTPMessageException(
            message="message url search parameter is required",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    if not message.endswith("valid"):
        raise HTTPMessageException(
            message="invalid message search parameter",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    context = {"message": message}
    return templates.TemplateResponse(
        request=request, name="verification_result.html", context=context
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
    invite_collection = get_collection(MONGO_COLLECTIONS.INVITE)
    if invite_collection is None:
        raise HTTPMessageException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=collection_error_msg(
                "get_single_event", MONGO_COLLECTIONS.INVITE.name
            ),
        )
    if (
        event := event_collection.find_one(
            {"_id": ObjectId(event_id), "created_by": current_user.id}
        )
    ) is None:
        raise HTTPMessageException(
            message="Event does not exist", status_code=status.HTTP_404_NOT_FOUND
        )

    event = EventModel(**event)
    invites = invite_collection.find({"event_invited_to": event.id}).to_list(1000)
    invite_coll = InviteCollection(invites=invites).model_dump()
    context = {"event": event.model_dump(), "invites": invite_coll["invites"]}
    return templates.TemplateResponse(
        request=request, name="event_details_page.html", context=context
    )
