# from mongocollection import MongoCollection
import discord
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
import pymongo

class DictObject(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self


class Post(DictObject):
    """Mongo Post class."""

class User(DictObject):
    """Mongo collection for a user."""
#     def __str__(self):
#         if hasattr(self, 'name'):
#             name = self.name
#         else:
#             name = type(self).__name__
#             l = [f'{k}={v}' for (k,v) in self.items()]
#         return name+"("+", ".join(l)+")"

    # def __init__(self, post:Post):
    #     """Mongo representation of a user."""
    #     self.user = user
        # self.post = post

    # @property
    # def id(self): return self.user.id

    # def getMoney(self):
    #     return self.post.money

    # def __getattribute__(self, att):
    #     collection = object.__getattribute__(self, 'collection')
    #     if att in collection:
    #         return collection[att]
    #     return super().__getattribute__(att)


    # def __setattr__(self, att, value):
    #     if hasattr(self, 'collection'):
    #         collection = object.__getattribute__(self, 'collection')
    #         collection[att] = value
    #     else:
    #         super().__setattr__(att, value)


class MongoCluster(MongoClient):
    """Rewrite of Mongo Client."""

    def __getitem__(self, item):
        item = super().__getitem__(item)
        if isinstance(item, pymongo.database.Database):
            return MongoDatabase.from_database(item)
        else:
            return item

class MongoDatabase(Database):
    @classmethod
    def from_database(cls, database):
        return cls(database.client, database.name)

    def __getitem__(self, item):
        item = super().__getitem__(item)
        if isinstance(item, pymongo.collection.Collection):
            return MongoCollection.from_collection(item)
        else:
            return item

class MongoCollection(Collection):
    keys = [
        '_BaseObject__codec_options',
        '_BaseObject__read_preference',
        '_BaseObject__write_concern',
        '_BaseObject__read_concern',
        '_Collection__database',
        '_Collection__name',
        '_Collection__full_name',
        '_Collection__write_response_codec_options'
    ]

    def put_once(self, **post):
        self.insert_one(post)

    def put(self, **post):
        if '_id' in post:
            id = post['_id']
            if id in self:
                self.replace_one({'_id':id}, post)
                return
        self.insert_one(post)

    def __contains__(self, id):
        return self.seek(_id=id)!=None

    def __len__(self):
        return len(list(self.find({})))

    def find_one(self, conditions):
        post = super().find_one(conditions)
        if post:
            return Post(post)
        return None

    @classmethod
    def from_collection(cls, collection):
        return cls(collection.database, collection.name)

    def seek(self, **conditions):
        return self.find(conditions)

    def seek_one(self, **conditions):
        return self.find_one(conditions)

    def __getitem__(self, id):
        return self.find_one({'_id':id})

    def __setitem__(self, id, value):
        self.post(id, value)

    def post(self, id, post):
        """Replace or insert a post."""
        self.replace_one({'_id':id}, post, upsert=True)
        # post = self.find_one({'_id':id})
        # value.update({'_id':id})
        # if post:
        #     self.replace_one({'_id':id}, value)
        # else:
        #     self.insert_one(value)

    def __setattr__(self, att, value):
        if att in type(self).keys:
            super().__setattr__(att, value)
        else:
            self.__setitem__(att, value)

# from config.config import mongo

# db['users'].find({'_id':id})['xp'] += 1
# db.users[id].xp+=1
# db.farm[id]
# db.bank[id].livret_a.money = 0
# db.bank[id].money += 123
# db.casino[id].coins += 34
# db.commands.append(command)
# command = db.commands.find(machin=34, bidule=324)

if __name__=="__main__":
    mongo_url = 'mongodb+srv://esclave:esclave@discord-cluster-5ckni.mongodb.net/test'
    cl = MongoCluster(mongo_url)
    # print('cluster over')
    esclave = cl.esclave
    # esclave = MongoDatabase.from_database(cl.esclave)
    print('main:', type(esclave))
    # memory = MongoCollection.from_collection(esclave.memory)
    memory = esclave.memory
    # print('main:', type(memory))
    # print(memory.seek_one(test='valeur'))
    # print('seeking')
    # print(memory.seek(test='valeur')[0])
    # print('memory.nope:', memory.nope)
    # memory.nope = {'is this a test?': 'yep'}
    # print(memory['nope'])
    # memory['test'] = {'this is':'a test'}
    # print('testing rn')
    # print(memory.test)
    # print(memory['test'])
    # memory['do i care'] = {'who cares':'not me'}
    # print(memory['do i care'])

    # d = {'a':1, 'b':2}
    # o = DictObject(d)
    # print(o)
    # memory.testing = {'testing':'testing'}
    memory.put(_id='testing', testing='testing')
    print(memory.testing.testing)
    # print(m)
    # user = User(d, 'marc')
    # print(user.a)
    # print(user.collection)
    # user.c = 3
    # print(user.collection)
    # print(user.__dict__)
    # marc = User(id=324, money=32)
    # print(marc)
    # marc.xp = 5
    # print(marc.keys())
    # del marc.id
    # marc.name = 'Marc'
    # print(marc.keys())
    # user = collection[id]
    # marc.xp+=1
    # print(marc)