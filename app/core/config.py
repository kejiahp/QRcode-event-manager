from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr, MongoDsn, computed_field
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    MONGO_USER: str
    MONGO_PASSWORD: str
    MONGO_HOST: str
    MONGO_QUERY: str

    DATABASE_NAME: str

    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: int
    CLOUDINARY_API_SECRET: str

    MAILING_EMAIL: EmailStr
    MAILING_PASSWORD: str

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


@lru_cache
def get_settings():
    return Settings()


settings: Settings = get_settings()
