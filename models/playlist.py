from discord.ext import commands
from .mongo import MongoCollection
import time
import discord

class Playlist:
    @classmethod
    def defaults(cls, ctx:commands.Context, title:str, music_cog:commands.Cog=None):
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

    def __init__(self,
            collection:MongoCollection,
            color=0xFFD700,
        ):
        self.collection = collection
        self.color = color

    def update(self, ctx:commands.Context):
        self.collection.setdefaults(**Playlist.defaults(ctx))

    @classmethod
    def create_musics(self, ctx:commands.Context, music_cog:commands.Cog=None):
        if music_cog:
            return dict(musics=music_cog.urls(ctx))
        else:
            return dict(musics=[])

    @classmethod
    def create_config(self, ctx:commands.Context, title:str):
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
                    'title': title,
                    'description': f"Playliste de {ctx.author.name}.",
                    'color': None,
                    'thumbnail': None,
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

    def embed(self, ctx:commands.Context):
        """Return a discord embed for the playlist."""
        c = self.collection
        description = c.config.description
        c.musics.musics
        if hasattr(c.config, 'title'):
            title = c.config.title
        else:
            title = 'sans titre'
        if hasattr(c.config, 'color'):
            color = c.config.color
        else:
            color = self.color
        em = discord.Embed(
            title=title,
            description=description or 'sans description',
            color=color,
        )
        author_names = [ctx.bot.get_user(id).name for id in c.config.owners]
        em.add_field(name='Auteurs', value=', '.join(author_names))
        if c.config.thumbnail:
            em.set_thumbnail(url=c.config.thumbnail)
        n = len(c.musics.musics)

        em.set_footer(text=f"{n} musiques")
        return em

    




