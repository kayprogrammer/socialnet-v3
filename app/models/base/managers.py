from datetime import datetime
from typing import Generic, List, Optional, Type, TypeVar
from uuid import UUID

from . tables import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseManager(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A Piccolo model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    async def get_all(self) -> Optional[List[ModelType]]:
        result = await self.model.select()
        return result

    async def get_all_ids(self) -> Optional[List[ModelType]]:
        result = await self.model.select(self.model.id)
        return result

    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        return await self.model.select().where(self.model.id == id)

    async def get_or_create(self, **kwargs):
        obj = None
        created = False
        if kwargs:
            obj = await self.model.select().where(kwargs)
        else:
            obj = await self.model.select().first()

        if not obj:
            obj = await self.create()
            created = True

        return obj, created
    
    async def create(
        self, obj_in: Optional[ModelType] = {}
    ) -> Optional[ModelType]:
        obj_in["created_at"] = datetime.utcnow()
        obj_in["updated_at"] = obj_in["created_at"]
        obj = (await self.model.insert(self.model(**obj_in)).returning(*self.model.all_columns()))[0]
        return obj

    async def bulk_create(self, obj_in: list) -> List[ModelType]:
        values = [self.model(**data) for data in obj_in]
        items = await self.model.insert(values).on_conflict(action="DO NOTHING").returning(*self.model.all_columns())
        return items

    async def update(
        self, id: UUID, obj_in: Optional[ModelType]
    ) -> Optional[ModelType]:
        data_to_update = {f'{self.model}.{key}': value for key, value in obj_in.items()} # This prefixes every key with the model. e.g Band.name, Band.age 
        data_to_update[self.model.updated_at] = datetime.utcnow()
        return await self.model.update().where(self.model.id == id).returning(*self.model.all_columns())

    async def delete(self, id: UUID):
        await self.model.delete().where(id == id)

    async def delete_all(self):
        await self.model.delete(force=True)

# class FileManager(BaseManager[File]):
#     pass


# file_manager = FileManager(File)