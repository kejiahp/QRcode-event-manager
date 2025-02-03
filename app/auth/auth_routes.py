from fastapi import APIRouter, status, Response
from .auth_models import CreateUserModel, PublicUserModel, UserModel
from .auth_dto import LoginUserDto
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.utils import Message, collection_error_msg, HTTPMessageException
from datetime import timedelta, datetime, timezone
from app.core import settings

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
        )

    if (user_exist := user_collection.find_one({"email": user_dto.email})) is not None:
        raise HTTPMessageException(
            status_code=400,
            message=f"User with email {user_exist["email"]} already exists in the system",
            success=False,
        )
    user_dto.hashed_password = get_password_hash(user_dto.hashed_password)
    user = UserModel(**user_dto.model_dump())
    result = user_collection.insert_one(user.model_dump())
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
        )
    if (user := user_collection.find_one({"email": login_dto.email})) is None:
        raise HTTPMessageException(
            status_code=404,
            message=f"user with email: {login_dto.email} does not exist in the system",
            success=False,
        )
    user = UserModel(**user)
    if not verify_password(login_dto.password, user.hashed_password):
        raise HTTPMessageException(
            status_code=400,
            message="Invalid credentials",
            success=False,
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
