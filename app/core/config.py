import secrets
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import (
    EmailStr,
    MongoDsn,
    computed_field,
    field_validator,
    BeforeValidator,
    AnyUrl,
    Field,
)
from functools import lru_cache
from typing import Any, Literal, Annotated


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    MONGO_USER: str
    MONGO_PASSWORD: str
    MONGO_HOST: str
    MONGO_QUERY: str
    MONGO_SCHEME: str

    DEBUG: bool

    DATABASE_NAME: str

    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: int
    CLOUDINARY_API_SECRET: str

    MAILING_EMAIL: EmailStr
    MAILING_PASSWORD: str

    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    # FRONTEND_HOST: str = "http://localhost:5173"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    # apply `parse_cors` before
    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = (
        []
    )

    @computed_field
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origins).rstrip("/") for origins in self.BACKEND_CORS_ORIGINS]

    # marking this as `computed_field` includes the property the serialized model result
    # this computed property isn't used in the project due to the structure of `pymongo`, though it is ideal when working with [moto](https://www.mongodb.com/developer/languages/python/python-quickstart-fastapi/?msockid=024877caef236b3220d76336ee406a42)
    @computed_field
    @property
    def PYMONGO_DATABASE_URI(self) -> MongoDsn:
        return MongoDsn.build(
            scheme="mongodb+srv",
            username=self.MONGO_USER,
            password=self.MONGO_PASSWORD,
            host=self.MONGO_HOST,
            query=self.MONGO_QUERY,
            # port="27017",
            # path="",
        )

    @field_validator("DEBUG")
    @classmethod
    def debug_str_to_bool(cls, value: Any):
        if isinstance(value, str):
            if value.lower() in {"true", "1", "yes"}:
                return True
            elif value.lower() in {"false", "0", "no"}:
                return False
            else:
                raise ValueError("Invalid `DEBUG` env")
        # the `bool` pydantic validator will do some type conversions
        return value


@lru_cache
def get_settings():
    return Settings()


settings: Settings = get_settings()
