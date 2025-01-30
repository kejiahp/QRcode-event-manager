from bson import ObjectId
from pydantic import BaseModel, Field, GetCoreSchemaHandler
from pydantic.json_schema import JsonSchemaValue


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
    success: bool
