from typing import Generic, TypeVar, List, Optional, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

# Type variable bound to Pydantic BaseModel to enforce validation schema types
T = TypeVar("T", bound=BaseModel)

class BaseRepository(Generic[T]):
    """
    Abstract Base Repository pattern implementation utilizing AsyncIOMotorClient collection mapping.
    Isolates data access layer logic from routes and heavy business services.
    """
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str, model_class: type[T]):
        self.db = db
        self.collection = db[collection_name]
        self.model_class = model_class

    async def create(self, entity: T) -> T:
        """
        Inserts a new validation-ready Pydantic model representation to MongoDB.
        """
        # Convert schema model fields to db-ready dict utilizing field aliases (mappings of id -> _id)
        data = entity.model_dump(by_alias=True)
        result = await self.collection.insert_one(data)
        # Update the entity instance with the assigned MongoDB ObjectId
        entity.id = result.inserted_id
        return entity

    async def get_by_id(self, id: Any) -> Optional[T]:
        """
        Retrieves a single record by its system ID, auto-casting valid string parameters.
        """
        if isinstance(id, str) and ObjectId.is_valid(id):
            id = ObjectId(id)
        doc = await self.collection.find_one({"_id": id})
        if doc:
            return self.model_class.model_validate(doc)
        return None

    async def get_all(self, filter_query: dict = None) -> List[T]:
        """
        Retrieves a list of records matching a standard database query filter.
        """
        filter_query = filter_query or {}
        cursor = self.collection.find(filter_query)
        results = []
        async for doc in cursor:
            results.append(self.model_class.model_validate(doc))
        return results

    async def update(self, id: Any, update_data: dict) -> bool:
        """
        Applies a patch command to modify fields in a single document matching the given ObjectId.
        """
        if isinstance(id, str) and ObjectId.is_valid(id):
            id = ObjectId(id)
        result = await self.collection.update_one({"_id": id}, {"$set": update_data})
        return result.modified_count > 0

    async def delete(self, id: Any) -> bool:
        """
        Removes a document from the collection matching the given ObjectId.
        """
        if isinstance(id, str) and ObjectId.is_valid(id):
            id = ObjectId(id)
        result = await self.collection.delete_one({"_id": id})
        return result.deleted_count > 0
