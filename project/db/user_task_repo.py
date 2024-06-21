from bson.objectid import ObjectId

class UserTaskDB:
    def __init__(self, mongo_db):
        self.collection = mongo_db.get_collection("user_tasks")

    async def create_user_task(self, user_id: str, task_id: str):
        result = await self.collection.insert_one({"user_id": user_id, "task_id": task_id})
        return str(result.inserted_id)

    async def get_user_task_by_task_id(self, task_id: str):
        user_task = await self.collection.find_one({"task_id": task_id})
        return user_task

    async def get_user_task_by_user_id(self, user_id: str):
        user_task = await self.collection.find_one({"user_id": user_id})
        return user_task

    async def delete_user_task_by_id(self, user_task_id: str):
        """Delete a user-task mapping by its ID."""
        result = await self.collection.delete_one({"_id": ObjectId(user_task_id)})
        return result.deleted_count

    async def delete_user_task_by_task_id(self, task_id: str):
        """Delete a user-task mapping by task ID."""
        result = await self.collection.delete_one({"task_id": task_id})
        return result.deleted_count

    async def delete_user_task_by_user_id(self, user_id: str):
        """Delete a user-task mapping by user ID."""
        result = await self.collection.delete_one({"user_id": user_id})
        return result.deleted_count
