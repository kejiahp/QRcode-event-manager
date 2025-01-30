from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field, ConfigDict, BeforeValidator
from datetime import datetime
from typing import Annotated, Optional

# Represents an ObjectId field in the database.
# It will be represented as a `str` on the model so that it can be serialized to JSON.
PyObjectId = Annotated[str, BeforeValidator(str)]


class UserBase(BaseModel):
    email: EmailStr = Field(max_length=255)
    hashed_password: str = Field(min_length=8, max_length=255)


class UserModel(UserBase):
    """
    Container for a single user record
    """

    # The primary key for the UserModel, stored as a `str` on the instance.
    # This will be aliased to `_id` when sent to MongoDB,
    # but provided as `id` in the API requests and responses.
    id: Optional[PyObjectId] = Field(
        alias="_id", default=None
    )  # `default=None` makes it optional
    password_reset_key: str | None = Field(default=None)
    is_active: bool = False
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        # json_schema_extra=
    )


class PublicUserModel(BaseModel):
    id: PyObjectId = Field(alias="_id")
    email: EmailStr
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(
        allow_population_by_field_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )


class CreateUserModel(UserBase):
    hashed_password: str = Field(min_length=8, max_length=40, alias="password")


class UpdateUserModel(BaseModel):
    """
    A set of optional update to be made to a document in the database
    """

    email: Optional[EmailStr] = None
    hashed_password: Optional[str] = None
    password_reset_key: Optional[str] = None
    is_active: Optional[bool] = None
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )
