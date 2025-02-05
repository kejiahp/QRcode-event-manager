import urllib.parse
import secrets
from fastapi import APIRouter, status, Response, Form, Request
from fastapi.responses import RedirectResponse
from .auth_models import (
    CreateUserModel,
    PublicUserModel,
    UserModel,
    UpdateUserEmail,
    UpdateUserPassword,
)
from typing import Annotated
from pymongo import ReturnDocument
from datetime import timedelta, datetime, timezone

from .auth_dto import LoginUserDto
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.utils import Message, collection_error_msg, HTTPMessageException
from app.core import settings
from app.core.mailing import generate_password_reset_email, send_email

from app.core import get_collection, MONGO_COLLECTIONS

router = APIRouter(prefix="/auth")


@router.post(
    "/sign-up",
    response_description="Add new User",
    status_code=status.HTTP_201_CREATED,
    response_model=Message,
)
def create_user(user_dto: CreateUserModel):
    """
    Create a new User
    """

    user_collection = get_collection(MONGO_COLLECTIONS.USERS)
    if user_collection is None:
        raise HTTPMessageException(
            status_code=500,
            message=collection_error_msg("create_user", MONGO_COLLECTIONS.USERS.name),
            success=False,
            json_res=True,
        )

    if (user_exist := user_collection.find_one({"email": user_dto.email})) is not None:
        raise HTTPMessageException(
            status_code=400,
            message=f"User with email {user_exist["email"]} already exists in the system",
            success=False,
            json_res=True,
        )
    user_dto.hashed_password = get_password_hash(user_dto.hashed_password)
    user = UserModel(**user_dto.model_dump())
    result = user_collection.insert_one(user.model_dump(by_alias=True, exclude=["id"]))
    new_user = user_collection.find_one({"_id": result.inserted_id})
    return Message(
        status_code=status.HTTP_201_CREATED,
        message="User created successfully",
        success=True,
        data=PublicUserModel(**new_user).model_dump(),
    )


@router.post(
    "/login",
    response_description="User login",
    status_code=status.HTTP_200_OK,
    response_model=Message,
)
def login(response: Response, login_dto: LoginUserDto):
    user_collection = get_collection(MONGO_COLLECTIONS.USERS)
    if user_collection is None:
        raise HTTPMessageException(
            status_code=500,
            message=collection_error_msg("login", MONGO_COLLECTIONS.USERS.name),
            success=False,
            json_res=True,
        )
    if (user := user_collection.find_one({"email": login_dto.email})) is None:
        raise HTTPMessageException(
            status_code=404,
            message=f"user with email: {login_dto.email} does not exist in the system",
            success=False,
            json_res=True,
        )
    user = UserModel(**user)
    if not verify_password(login_dto.password, user.hashed_password):
        raise HTTPMessageException(
            status_code=400, message="Invalid credentials", success=False, json_res=True
        )
    user = PublicUserModel(**user.model_dump())
    user = user.model_dump()
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_tkn = create_access_token(user.get("id"), expires_delta=access_token_expires)
    user["token"] = access_tkn

    cookie_exp = datetime.now(timezone.utc) + access_token_expires
    response.set_cookie(key="tk", value=access_tkn, expires=cookie_exp, httponly=True)

    return Message(
        status_code=status.HTTP_200_OK,
        message="User authenitcation successful",
        success=True,
        data=user,
    )


@router.post("/send-password-reset-email", name="send_password_reset_email")
def send_password_reset_email(
    request: Request, user_email: Annotated[UpdateUserEmail, Form()]
):
    user_collection = get_collection(MONGO_COLLECTIONS.USERS)
    if user_collection is None:
        raise HTTPMessageException(
            status_code=500,
            message=collection_error_msg(
                "send_password_reset_email", MONGO_COLLECTIONS.USERS.name
            ),
            success=False,
        )

    if (user := user_collection.find_one({"email": user_email.email})) is None:
        raise HTTPMessageException(status_code=404, message="user does not exist")

    reset_code = f"reset_{secrets.token_urlsafe(20)}"

    user_collection.find_one_and_update(
        {"_id": user["_id"]},
        {"$set": {"password_reset_key": reset_code}},
        return_document=ReturnDocument.AFTER,
    )

    search_params_obj = {"email": user_email.email}

    redirect_url = f"{request.url_for("forgot_password")}?{urllib.parse.urlencode(search_params_obj)}"

    search_params_obj["reset_code"] = reset_code

    reset_url = f"{request.url_for("forgot_password")}?{urllib.parse.urlencode(search_params_obj)}"

    try:
        email_data = generate_password_reset_email(password_reset_link=reset_url)

        send_email(
            email_to=user_email.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    except Exception as exc:
        print("#### FAILED TO SEND PASSWORD RESET MAIL ####")
        print(exc)
        print("#### FAILED TO SEND PASSWORD RESET MAIL ####")

        raise HTTPMessageException(
            message=(
                exc.message if hasattr(exc, "message") else "Something went wrong"
            ),
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            success=False,
        )

    return RedirectResponse(status_code=status.HTTP_302_FOUND, url=redirect_url)


@router.post("/update-password", name="update_user_password")
def update_user_password(
    request: Request,
    user_password: Annotated[UpdateUserPassword, Form()],
):
    user_collection = get_collection(MONGO_COLLECTIONS.USERS)
    if user_collection is None:
        raise HTTPMessageException(
            status_code=500,
            message=collection_error_msg(
                "send_password_reset_email", MONGO_COLLECTIONS.USERS.name
            ),
            success=False,
        )

    hashed_password = get_password_hash(user_password.password)

    user_with_code = user_collection.find_one_and_update(
        {"password_reset_key": user_password.reset_code},
        {"$set": {"password_reset_key": None, "hashed_password": hashed_password}},
        return_document=ReturnDocument.AFTER,
    )

    if user_with_code is None:
        raise HTTPMessageException(
            message="User with this reset code does not exist",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    reseponse = RedirectResponse(
        status_code=status.HTTP_302_FOUND, url=request.url_for("auth")
    )
    reseponse.delete_cookie(key="tk")
    return reseponse


@router.get("/logout", name="logout")
def logout(request: Request):
    reseponse = RedirectResponse(
        status_code=status.HTTP_302_FOUND, url=request.url_for("auth")
    )
    reseponse.delete_cookie(key="tk")
    return reseponse
