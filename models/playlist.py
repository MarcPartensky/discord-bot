from discord.ext import commands
from .mongo import MongoCollection
import time

class Playlist:
    @classmethod
    def defaults(cls, ctx:commands.Context):
        return dict(
            musics = cls.create_musics(ctx),
            options = cls.create_options(ctx),
            memory = cls.create_memory(ctx),
            historic = [],
            comments = [],
            propositions = [],
        )

    rights = [
        'r', # read
        'e', # edit
        'w', # write
        'd', # delete
        'a', # add
        'l', # listen
        'm', # master
    ]

    @classmethod
    def create(cls, ctx:commands.Context, collection:MongoCollection, description:str=None):
        collection.setdefaults(Playlist.defaults(ctx))
        return cls(collection)

    @classmethod
    def load(cls, ctx:commands.Context, collection:MongoCollection):
        collection.setdefaults(**Playlist.defaults(ctx))
        return cls(collection)

    def __init__(self, collection:MongoCollection):
        self.collection = collection

    def __getattribute__(self, key):
        if key.startswith('_'):
            return getattr(self, key)
        else:
            return getattr(self.collection, key)

    def __setattr__(self, key, value):
        setattr(self.collection, key, value)

    def update(self, ctx:commands.Context):
        self.collection.setdefaults(**Playlist.defaults(ctx))

    @classmethod
    def create_musics(self, ctx:commands.Context):
        return ctx.get_cog('Music').urls(ctx)

    @classmethod
    def create_options(self, ctx:commands.Context):
        return {
                    'roles': {
                        'owners': [ctx.author.id],
                        'collaborators': [],
                    },
                    'rights': {
                        'owners': 'rewdalm',
                        'collaborators': 'rewdal',
                        'everyone': 'rl',
                    },
                    'description': f"Playliste de {ctx.author.name}."
                }

    @classmethod
    def create_memory(self, ctx:commands.Context):
        return {
                'author': ctx.author.id,
                'created': time.time(),
            }

    def get_role(self, user_id:int):
        for [role, user_ids] in self.options.roles:
            if user_id in user_ids:
                return role
        return 'everyone'
    
    def get_rights(self, user_role:str):
        for [role, rights] in self.options.rights:
            if user_role == role:
                return rights
        return []

    def get_user_rights(self, user_id:int):
        role = self.get_role(user_id)
        return self.get_rights(role)

    def has_right(self, user_id:int, *rights:str):
        user_rights = self.get_user_rights(user_id)
        for right in rights:
            if not right in user_rights:
                return False
        return True



