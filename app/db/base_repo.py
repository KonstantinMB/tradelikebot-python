# base_repo.py
from motor.motor_asyncio import AsyncIOMotorClient

class MongoDB:
    def __init__(self, uri, db_name):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[db_name]

    def get_collection(self, collection_name):
        return self.db[collection_name]

    async def fetch_one(self, collection, query):
        document = await self.db[collection].find_one(query)
        if document:
            document['_id'] = str(document['_id'])
        return document

    async def fetch_all(self, collection, query):
        cursor = self.db[collection].find(query)
        documents = await cursor.to_list(length=None)
        for document in documents:
            document['_id'] = str(document['_id'])
        return documents

    async def create(self, collection, document):
        result = await self.db[collection].insert_one(document)
        return str(result.inserted_id)

    async def update(self, collection, query, update_values):
        result = await self.db[collection].update_one(query, {'$set': update_values})
        return result.modified_count

    async def delete(self, collection, query):
        result = await self.db[collection].delete_one(query)
        return result.deleted_count
