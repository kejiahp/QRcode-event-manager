from bson import ObjectId
from pydantic import BaseModel, Field, GetCoreSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from typing import Dict, Union, Any
from fastapi.exceptions import HTTPException


# Helper class for MongoDB ObjectId
# Not used though inserted for reference
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(clssRef, value_to_validate):
        if not ObjectId.is_valid(value_to_validate):
            raise ValueError("Invalid ObjectId")
        return ObjectId(value_to_validate)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, schema: JsonSchemaValue, handler: GetCoreSchemaHandler
    ) -> JsonSchemaValue:
        # Define the JSON schema representation for ObjectId
        schema = handler(schema)
        schema.update(type="string")
        return schema

    @classmethod
    def __get_pydantic_core_schema__(cls, source, handler: GetCoreSchemaHandler):
        # Use the core schema to validate ObjectId
        return handler(str)  # Treat ObjectId as a string for validation


class Message(BaseModel):
    message: str
    status_code: int
    success: bool
    data: Union[Dict[str, Any], list, None] = None


class TokenPayload(BaseModel):
    exp: int
    sub: str


class HTTPMessageException(HTTPException):
    def __init__(
        self,
        status_code,
        message: str,
        success: bool,
        headers=None,
    ):
        _detail = Message(
            message=message, status_code=status_code, success=success, data=None
        )
        _detail = _detail.model_dump()
        del _detail["data"]
        super().__init__(status_code, _detail, headers)


def collection_error_msg(func_name: str, collection_name: str) -> str:
    return f"[{func_name}]: Collection with name: {collection_name} was not found."
