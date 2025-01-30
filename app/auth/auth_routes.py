from bson import ObjectId
from fastapi import APIRouter, HTTPException, status
from .auth_models import CreateUserModel, PublicUserModel, UserModel
from app.core.security import get_password_hash
from app.core.utils import Message

from app.core import get_collection, MONGO_COLLECTIONS

router = APIRouter(prefix="/auth")


@router.post(
    "/sign-up",
    response_description="Add new User",
    status_code=status.HTTP_201_CREATED,
    response_model=PublicUserModel,
)
def create_user(user_dto: CreateUserModel):
    """
    Create a new User
    """

    user_collection = get_collection(MONGO_COLLECTIONS.USERS)
    if user_collection is None:
        raise HTTPException(
            status_code=500,
            detail=f"[create_user]: Collection with name: {MONGO_COLLECTIONS.USERS.name} was not found.",
        )

    if (user_exist := user_collection.find_one({"email": user_dto.email})) is not None:
        raise HTTPException(
            status_code=400,
            detail=f"User with email {user_exist["email"]} already exists in the system",
        )
    user_dto.hashed_password = get_password_hash(user_dto.hashed_password)
    user = UserModel(**user_dto.model_dump())
    result = user_collection.insert_one(user.model_dump())
    new_user = user_collection.find_one({"_id": result.inserted_id})
    return PublicUserModel(**new_user)


"""
def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user

"""
