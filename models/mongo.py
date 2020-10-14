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


class MongoCluster(MongoClient):
    """Rewrite of Mongo Client."""

    def __getitem__(self, item):
        """Return a mongo database given its key."""
        item = super().__getitem__(item)
        if isinstance(item, pymongo.database.Database):
            return MongoDatabase.from_database(item)
        else:
            return item

    def __delitem__(self, key):
        self.drop_database(key)


class MongoDatabase(Database):
    @classmethod
    def from_database(cls, database):
        """Create a mongo database using another mongo database."""
        return cls(database.client, database.name)

    def __getitem__(self, item):
        """Return a mongo collection given a key."""
        item = super().__getitem__(item)
        if isinstance(item, pymongo.collection.Collection):
            return MongoCollection.from_collection(item)
        else:
            return item

    def __delitem__(self, collection_name):
        """Drop a collection using its name."""
        self.drop_collection(collection_name)

    def __contains__(self, collection_name):
        """Check whether the mongo database has a collection given its name."""
        return collection_name in self.collection_names()

    def __len__(self):
        """Count the number of collections."""
        return len(self.list_collection_names())

    def items(self):
        """List the items in a database."""
        return zip(
            self.list_collection_names(),
            map(lambda name:MongoCollection(self, name), self.list_collection_names())
            )

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

    def __iter__(self):
        """Iterate through the connexion."""
        return map(lambda d:BindPost(_id=d['_id'], _collection=self), self.find())

    def items(self):
        """Liste les items."""
        for post in self.find():
            yield (post['_id'], BindPost(_collection=self, _id=post['_id']))

    def put_one(self, **post):
        """Insert one post."""
        self.insert_one(post)

    def put(self, **post):
        """Insert or replace one post."""
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
        """Replace one post."""
        post = self.treat(post)
        super().replace_one(filter, post, **kwargs)

    def insert_one(self, post, **kwargs):
        """Insert one post."""
        post = self.treat(post)
        super().insert_one(post, **kwargs)

    def insert(self, arg, **kwargs):
        if isinstance(arg, list) or isinstance(arg, tuple):
            self.insert_many(arg, **kwargs)
        else:
            self.insert_one(arg, **kwargs)

    def insert_many(self, posts, **kwargs):
        """Insert many posts."""
        posts = [self.treat(post) for post in posts]
        super().insert_many(post)

    def __contains__(self, id):
        return self.seek_one(_id=id)!=None

    def __len__(self):
        """Determine the length of the collection."""
        return self.count_documents({})

    def lazy_get(self, id):
        """Return a bind post."""
        return BindPost(_collection=self, _id=id)

    @classmethod
    def from_collection(cls, collection):
        """Make a collection from a collection."""
        return cls(collection.database, collection.name)

    def seek(self, **conditions):
        """Easier to use find method."""
        return self.find(conditions)

    def seek_one(self, **conditions):
        """Easier to use find_one method."""
        return self.find_one(conditions)

    def __getitem__(self, id):
        """Lazy way of getting posts."""
        return self.lazy_get(id)

    def __setitem__(self, id, post):
        """Lazy way of settings posts."""
        post['_id'] = id
        self.post(post)

    def __delitem__(self, id):
        """Delete a post."""
        print(id)
        print(self.find_one(dict(_id=id)))
        self.delete_one(dict(_id=id))
        print(self.find_one(dict(_id=id)))

    def post(self, post):
        """Replace or insert a post."""
        if '_id' in post:
            self.replace_one({'_id':post['_id']}, post, upsert=True)
        else:
            self.insert_one(post)

    def setdefaults(self, *args, **kwargs):
        """Set defaults posts."""
        dicts = args+(kwargs,)
        for d in dicts:
            for k,v in d.items():
                self.setdefault(k, v)

    def setdefault(self, id, post):
        """Set a default post."""
        if id in self:
            post.update(self[id]._dict)
        print(1, post)
        self[id] = post
        print(2, self[id])

    def __setattr__(self, att, value):
        if att in type(self).keys or att in dir(self):
            super().__setattr__(att, value)
        else:
            self.__setitem__(att, value)

class BindPost: # More like lazy post
    """Super set of mongo post system.
    Instead of using a mongo post as a python dictionary, this class makes
    it possible to use a post as a python object which allows much more
    flexibility when writing code."""

    @classmethod
    def fromkeys(cls, *args, **kwargs):
        """Create a bind post from keys."""
        return cls(MongoCollection.fromkeys(*args, **kwargs))

    def __init__(self, _collection:MongoCollection,  _id:object=None):
        """Create a bind post using a mongo collection and a post id."""
        self._collection:MongoCollection = _collection
        if _id:
            self._id = _id
        else:
            self._id = ObjectId()
        if not self._dict:
            d = dict(_id=self._id)
            self._collection.insert_one(d)

    @property
    def collection(self) -> MongoCollection:
        """Return the mongo collection parent of the post."""
        return self._collection

    @property
    def _dict(self) -> dict:
        """Return the dictionary form of the post."""
        return Collection.find_one(self._collection, {'_id':self._id})

    def clear(self):
        """Clear the content of a post."""
        d = dict(_id=self._id)
        self._collection.replace_one(d, d)

    def copy(self) -> dict: # Create raw dictionary
        """Create a raw dictionary."""
        return self._dict.copy()

    def get(self, key):
        """Get an item of the post given a key."""
        return self._dict[key]

    def items(self):
        """List the items of the post."""
        return self._dict.items()

    def keys(self):
        """List the keys of the post."""
        return self._dict.keys()

    def values(self):
        """List the values of the post."""
        return self._dict.values()

    def pop(self, key):
        """Pop one item of the post given its key."""
        d = self._dict
        item = d.pop(key)
        self._collection.replace_one({'_id':self._id}, d)
        return item

    def popitem(self):
        """Pop the last item of the dictionary."""
        dictionary = self._dict.copy()
        item = dictionary.popitem()
        return item

    def setdefault(self, key, value):
        """Set a default item using its key and value."""
        d = self._dict
        d.setdefault(key, value)
        self._collection.replace_one({'_id':self._id}, d)

    def setdefaults(self, *args, **kwargs):
        """Set default items using the list of items, and dictionaries
        of keys and values of the items."""
        dicts = args+(kwargs,)
        for d in dicts:
            for k,v in d.items():
                self.setdefault(k, v)

    def update(self, _dictionary:dict):
        """Update a post using a dictionary."""
        d = self._dict
        d.update(_dictionary)
        self._collection.replace_one({'_id':self._id}, d)

    def __str__(self) -> str:
        """Return a string representation of the post."""
        return str(self._dict)

    def __contains__(self, key) -> bool:
        """Check whether the post contains a key."""
        return key in self._dict

    def __delattr__(self, key):
        """Delete an item from the post given its key."""
        print('before:', self)
        self._collection.update_one({'_id':self._id}, {"$unset": {key:""}})
        print('after:', self)

    __delitem__ = __delattr__

    def __getattribute__(self, key):
        """Return the value of a post item given its key."""
        if key in ['_collection', '_id', 'collection', '_dict']:
            return super().__getattribute__(key)
        else:
            d = self._dict
            if key in d:
                return d[key]
            else:
                return super().__getattribute__(key)

    def __setattr__(self, key, value):
        """Set an item for the post given its key and value."""
        if key in ['_collection', '_id']:
            super().__setattr__(key, value)
        else:
            d = self._dict
            d[key] = value
            self._collection.replace_one({'_id':self._id}, d)

    def __getitem__(self, key):
        """Return the value of an item given its key.
        This can be used the same way as a dictionary."""
        return getattr(self, key)
        # return self._dict[key]
        # return self._collection[key]

    def __setitem__(self, key, value):
        """Set an item for the post given its key and value.
        This can be used the same was as a dictionary."""
        setattr(self, key, value)
        # d = self._dict
        # d[key] = value
        # self._collection.replace_one({'_id':self._id}, d)

    def __len__(self):
        """Return the length of a post."""
        return len(self._dict)

class Post(DictObject):
    """Mongo Post class."""
    def __setattr__(self, key, value):
        self[key] = value
        self.post()

    def __str__(self):
        """Return the string representation of a post."""
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
