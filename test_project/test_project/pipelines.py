import pymongo
from itemadapter import ItemAdapter
import os

class MongoPipeline:
    collection_name = "scrapy_items"

    def __init__(self, mongo_uri, mongo_db,mongo_db_collection):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_db_collection = mongo_db_collection

    @classmethod
    def from_crawler(cls, crawler):
        mongo_db = crawler.settings.get("MONGO_DB", "books")
        mongo_user = crawler.settings.get("MONGO_USER")
        mongo_host = crawler.settings.get("MONGO_HOST","localhost")
        mongo_password = crawler.settings.get("MONGO_PASSWORD")
        mongo_port = crawler.settings.get("MONGO_PORT", 27017)
        mongo_db_collection = crawler.settings.get("MONGO_DB_COLLECTION","items")
        mongo_uri = f"mongodb://{mongo_user}:{mongo_password}@localhost"
        
        return cls(
            mongo_uri=mongo_uri,
            mongo_db=mongo_db, mongo_db_collection=mongo_db_collection)

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        
        self.db[self.mongo_db_collection].insert_one(ItemAdapter(item).asdict())
        return item
    