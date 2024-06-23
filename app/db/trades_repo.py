from bson.objectid import ObjectId
import logging
logger = logging.getLogger(__name__)

class TradeDB:
    def __init__(self, mongo_db):
        self.collection = mongo_db.get_collection("trades")

    async def get_total_investment_by_user(self, user_id: str):
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": "$user_id",
                "total_investment": {
                    "$sum": "$quantity"
                }
            }}
        ]
        result = await self.collection.aggregate(pipeline).to_list(None)
        logger.info(result)
        if result:
            return result[0]['total_investment']
        return 0

    async def get_trade_by_task_id(self, task_id: str):
        return await self.collection.find_one({"task_id": task_id})

    async def delete_trade_by_id(self, trade_id: str):
        result = await self.collection.delete_one({"_id": ObjectId(trade_id)})
        return result.deleted_count

    async def create_trade(self, trade_data: dict):
        result = await self.collection.insert_one(trade_data)
        inserted_id = result.inserted_id
        return str(inserted_id)

    async def get_all_trades_by_user_id(self, user_id: str):
        cursor = self.collection.find({"user_id": user_id})
        trades = await cursor.to_list(length=None)
        return trades

    async def get_trade_by_user_id(self, user_id: str):
        trade = await self.collection.find_one({"user_id": user_id})
        return trade

    async def get_all_trades(self):
        cursor = self.collection.find()
        trades = await cursor.to_list(length=None)
        return trades

    async def update_trade(self, trade_id: str, update_data: dict):
        result = await self.collection.update_one({"_id": ObjectId(trade_id)}, {"$set": update_data})
        return result.modified_count

    async def delete_trade_by_user_id(self, user_id: str):
        result = await self.collection.delete_many({"user_id": user_id})
        return result.deleted_count
