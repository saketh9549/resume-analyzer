from typing import Annotated
from bson import ObjectId
from pydantic import BaseModel, BeforeValidator, PlainSerializer, Field, ConfigDict

# Custom Pydantic v2 type for handling MongoDB's ObjectId
# Validates string format of ObjectId and serializes to string representation
def validate_object_id(v: any) -> ObjectId:
    if isinstance(v, ObjectId):
        return v
    if isinstance(v, str) and ObjectId.is_valid(v):
        return ObjectId(v)
    raise ValueError("Invalid ObjectId format")

PyObjectId = Annotated[
    ObjectId,
    BeforeValidator(validate_object_id),
    PlainSerializer(lambda x: str(x), return_type=str)
]

class MongoBaseModel(BaseModel):
    """
    Base model for MongoDB documents that automatically maps '_id' to 'id'.
    """
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )
