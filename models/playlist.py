from discord.ext import commands
from .mongo import MongoCollection
import time

class Playlist:
    @classmethod
    def defaults(cls, ctx:commands.Context, music_cog:commands.Cog=None):
        return dict(
            musics = cls.create_musics(ctx, music_cog),
            config = cls.create_config(ctx),
            memory = cls.create_memory(ctx),
            historic = dict(historic=[]),
            comments = dict(comments=[]),
            propositions = dict(propositions=[]),
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
    def create(cls, ctx:commands.Context, collection:MongoCollection, music_cog:commands.Cog, description:str=None):
        defaults = Playlist.defaults(ctx, music_cog)
        print(defaults)
        collection.setdefaults(**defaults)
        return cls(collection)

    @classmethod
    def load(cls, ctx:commands.Context, collection:MongoCollection):
        collection.setdefaults(**Playlist.defaults(ctx))
        return cls(collection)

    def __init__(self, collection:MongoCollection):
        self.collection = collection

    def update(self, ctx:commands.Context):
        self.collection.setdefaults(**Playlist.defaults(ctx))

    @classmethod
    def create_musics(self, ctx:commands.Context, music_cog:commands.Cog=None):
        if music_cog:
            return dict(musics=music_cog.urls(ctx))
        else:
            return dict(musics=[])

    @classmethod
    def create_config(self, ctx:commands.Context):
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
        for role, user_ids in self.collection.config.roles.items():
            if user_id in user_ids:
                return role
        return 'everyone'
    
    def get_rights(self, user_role:str):
        for [role, rights] in self.collection.config.rights.items():
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



