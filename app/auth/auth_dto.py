from pydantic import BaseModel, EmailStr, Field
from .auth_models import PublicUserModel


class LoginUserDto(BaseModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=255)


class LoginUserResponse(PublicUserModel):
    token: str
