import secrets
from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict, EmailStr, HttpUrl
from datetime import datetime
from typing import Union, List, Optional

from app.auth.auth_models import PyObjectId
from app.core.utils import PyObjectId as PyObjectIdV2


class EventModel(BaseModel):
    """
    Single event document model
    """

    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str = Field(max_length=255)
    code: str = Field(default_factory=lambda: secrets.token_urlsafe(5))
    description: str
    start_date: datetime
    end_date: datetime
    is_active: bool = True
    created_by: PyObjectId
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )


class UpdateEventModel(BaseModel):
    """
    Event update validation schema
    """

    name: str = Field(max_length=255)
    description: str
    start_date: datetime
    end_date: datetime

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )


class CreateEventModel(BaseModel):
    """
    Creation of events
    """

    name: str = Field(max_length=255)
    description: str
    start_date: datetime
    end_date: datetime


class EventCollection(BaseModel):
    events: List[EventModel]


class InviteModel(BaseModel):
    id: Optional[PyObjectIdV2] = Field(alias="_id", default=None)
    email: EmailStr = Field(max_length=255)
    fullname: str
    event_invited_to: PyObjectIdV2
    code: str
    qr_code_img: HttpUrl
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )


class CreateInviteModel(BaseModel):
    email: EmailStr = Field(max_length=255)
    fullname: str
