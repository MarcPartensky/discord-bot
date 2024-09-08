# from config.tools import DictObject
# from config.config import mongo_url

from ..config.config import mongo_url

print(mongo_url)

from pymongo import MongoClient


class MongoDatabase(MongoClient):
    def __getattribute__(self, att):

        if hasattr(self, att):
            return att

        att = super().__getattribute__(att)
        return MongoCollection()


class MongoCollection:
    pass


if __name__ == "__main__":
    db = MongoDatabase(mongo_url)
