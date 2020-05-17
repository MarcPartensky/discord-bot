# from mongocollection import MongoCollection
import discord

class User(DictObject)
    def __str__(self):
        if hasattr(self, 'name'):
            name = self.name
        else:
            name = type(self).__name__
        return name+"("+", ".join(f"{k}={v}" for k,v in self.items())+")"


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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.users = Users(self['users'])

class Users(MongoCollection):
    pass


from config.config import mongo
cluster.users[id].xp+=1
cluster.farm[id]
cluster.bank[id].livret_a.money = 0
cluster.bank[id].money += 123
cluster.casino[id].coins += 34
cluster.commands.append(command)
cluster.commands.find(machin=34, bidule=324)






if __name__=="__main__":
    # d = {'a':1, 'b':2}
    # user = User(d, 'marc')
    # print(user.a)
    # print(user.collection)
    # user.c = 3
    # print(user.collection)
    # print(user.__dict__)
    marc = User(id=324, money=32)
    print(marc)
    marc.xp = 5
    print(marc.keys())
    del marc.id
    marc.name = 'Marc'
    print(marc.keys())


    # user = collection[id]
    marc.xp+=1
    print(marc)

