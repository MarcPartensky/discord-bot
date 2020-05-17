from config.tools import DictObject
from config.config import mongo_url

from pymongo import MongoClient

class MongoDatabase(MongoClient, DictObject):
    def __getattribute__(self, att):
        if hasattr(self, att):
            return att
        
        att = super().__getattribute__(att)
        return MongoCollection()

if __name__=='__main__':
    db = MongoDatabase()