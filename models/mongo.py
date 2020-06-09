# from mongocollection import MongoCollection
import discord
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.son_manipulator import ObjectId
import pymongo

# from pymongo.cursor import Cursor

class DictObject(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        super().__setattr__('__dict__', self)

class CommitPost:
    
    @classmethod
    def fromkeys(cls, *args, **kwargs):
        return cls(_dict.fromkeys(*args, **kwargs))

    def __init__(self, *args, **kwargs):
        self._collection = kwargs.pop('_collection')
        self._dict = dict(*args ,**kwargs)
        self.post()

    def clear(self):
        self._dict.clear()

    def copy(self):
        return self._dict.copy()

    def get(self, key):
        return self._dict.get(key)

    def items(self):
        return self._dict.items()

    def keys(self):
        return self._dict.keys()

    def values(self):
        return self._dict.values()

    def pop(self, key):
        return self._dict.pop(key)

    def popitem(self):
        return self._dict.popitem()

    def setdefault(self, key, value):
        self._dict.setdefault(key, value)

    def setdefaults(self, *args, **kwargs):
        dicts = args+(kwargs,)
        for dict_ in dicts:
            self._dict.update(dict_)
            # for k,v in d.items():
            #     self.setdefault(k, v)

    def update(self, dictionary_:dict):
        self._dict.update(dictionary_)

    def __str__(self):
        return str(self._dict)

    def __contains__(self, key):
        return key in self._dict

    def __getattribute__(self, key):
        if key in ['_collection', '_dict']:
            return super().__getattribute__(key)
        else:
            if key in self._dict:
                return self._dict[key]
            else:
                return super().__getattribute__(key)

    def __setattr__(self, key, value):
        if key in ['_collection', '_dict']:
            super().__setattr__(key, value)
        else:
            self._dict[key] = value
            self.post()

    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, value):
        self._dict[key] = value

    def __len__(self):
        return len(self._dict)

    def post(self):
        self._collection.post(self._dict)

class BindPost:
    @classmethod
    def fromkeys(cls, *args, **kwargs):
        return cls(_dict.fromkeys(*args, **kwargs))

    def __init__(self, *args, **kwargs):
        if args: kwargs.update(args[0])
        self._collection:MongoCollection = kwargs.pop('_collection')
        if '_id' in kwargs:
            self._id = kwargs.get('_id')
        else:
            self._id = ObjectId()
        if not self._dict:
            d = {'_id':self._id}
            self._collection.insert_one(d)

    @property
    def collection(self):
        return self._collection

    @property
    def _dict(self):
        return Collection.find_one(self._collection, {'_id':self._id})

    def clear(self):
        d = {'_id':self._id}
        self._collection.replace_one(d, d)

    def copy(self): # Create raw dictionary
        return self._dict.copy()

    def get(self, key):
        return self._dict[key]

    def items(self):
        return self._dict.items()

    def keys(self):
        return self._dict.keys()

    def values(self):
        return self._dict.values()

    def pop(self, key):
        d = self._dict
        item = d.pop(key)
        self._collection.replace_one({'_id':self._id}, d)
        return item

    def popitem(self):
        dictionary = self._dict.copy()
        item = dictionary.popitem()
        return item

    def setdefault(self, key, value):
        d = self._dict
        d.setdefault(key, value)
        self._collection.replace_one({'_id':self._id}, d)

    def setdefaults(self, *args, **kwargs):
        dicts = args+(kwargs,)
        for d in dicts:
            for k,v in d.items():
                self.setdefault(k, v)

    def update(self, _dictionary:dict):
        d = self._dict
        d.update(_dictionary)
        self._collection.replace_one({'_id':self._id}, d)

    def __str__(self):
        return str(self._dict)

    def __contains__(self, key):
        return key in self._dict

    def __delattr__(self, key):
        self._collection.update_one({'_id':self._id}, {"$unset": {key:""}})

    __delitem__ = __delattr__

    def __getattribute__(self, key):
        if key in ['_collection', '_id', 'collection', '_dict']:
            return super().__getattribute__(key)
        else:
            d = self._dict
            if key in d:
                return d[key]
            else:
                return super().__getattribute__(key)

    def __setattr__(self, key, value):
        if key in ['_collection', '_id']:
            super().__setattr__(key, value)
        else:
            d = self._dict
            d[key] = value
            self._collection.replace_one({'_id':self._id}, d)

    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, value):
        self._dict[key] = value

    def __len__(self):
        return len(self._dict)

class Post(DictObject):
    """Mongo Post class."""
    def __setattr__(self, key, value):
        self[key] = value
        self.post()

    def __str__(self):
        collection = self.collection
        del self.collection
        string = super().__str__()
        super().__setattr__('collection', collection)
        return string

    def post(self):
        """Post a post."""
        collection = self.pop('collection')
        collection[self._id] = self
        super().__setattr__('collection', collection)


class SuperPost(DictObject):
    """Pass"""

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

    def treat(self, post):
        p = post.copy()
        if 'collection' in post:
            p.pop('collection')
        return p

    def replace_one(self, filter, post, **kwargs):
        post = self.treat(post)
        super().replace_one(filter, post, **kwargs)

    def insert_one(self, post, **kwargs):
        post = self.treat(post)
        super().insert_one(post, **kwargs)

    def insert(self, arg, **kwargs):
        if isinstance(arg, list) or isinstance(arg, tuple):
            self.insert_many(arg, **kwargs)
        else:
            self.insert_one(arg, **kwargs)

    def insert_many(self, posts, **kwargs):
        posts = [self.treat(post) for post in posts]
        super().insert_many(post)

    def __contains__(self, id):
        return self.seek(_id=id)!=None

    def __len__(self):
        return self.count_documents({})

    def find_one(self, conditions, **kwargs):
        post = super().find_one(conditions, **kwargs)
        if post:
            post = BindPost(post, _collection=self)
        else:
            post = BindPost(conditions, _collection=self)
        return post

    @classmethod
    def from_collection(cls, collection):
        return cls(collection.database, collection.name)

    def seek(self, **conditions):
        return self.find(conditions)

    def seek_one(self, **conditions):
        return self.find_one(conditions)

    def __getitem__(self, id):
        return self.find_one({'_id':id})

    def __setitem__(self, id, post):
        post['_id'] = id
        self.post(post)

    def post(self, post):
        """Replace or insert a post."""
        if '_id' in post:
            self.replace_one({'_id':post['_id']}, post, upsert=True)
        else:
            self.insert_one(post)

    def __setattr__(self, att, value):
        if att in type(self).keys:
            super().__setattr__(att, value)
        else:
            self.__setitem__(att, value)

    # def find(self, *args, **kwargs):
    #     cursor = super().find(*args, **kwargs)
    #     return map(Post, cursor)

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