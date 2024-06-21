from bson.objectid import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection

class UserDB:
    def __init__(self, mongo_db):
        self.collection = mongo_db.get_collection("users")

    async def create_user(self, user_data: dict):
        """Create a new user."""
        result = await self.collection.insert_one(user_data)
        return str(result.inserted_id)

    async def get_user_by_id(self, user_id: str):
        """Retrieve a user by their ID."""
        user = await self.collection.find_one({"_id": ObjectId(user_id)})
        return user

    async def get_all_users(self):
        """Retrieve all users."""
        cursor = self.collection.find()
        users = await cursor.to_list(length=None)
        return users

    async def update_user(self, user_id: str, update_data: dict):
        """Update user information."""
        result = await self.collection.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
        return result.modified_count

    async def delete_user(self, user_id: str):
        """Delete a user by their ID."""
        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count
