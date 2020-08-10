import discord
import asyncio

from discord.ext import commands
from config.config import access
from models.mongo import MongoDatabase, MongoCollection, BindPost
from config import emoji


class MongoRoom:
    def __init__(self,
                 member: discord.Member,
                 collection: MongoCollection = None,
                 database: MongoDatabase = None,
                 post: BindPost = None,
                 message: discord.Message = None,
                 timeout = 60,
                 ):
        """Create a mongo room using the member, the actual collection and the database."""
        self.member = member
        self.collection = collection
        self.post = post
        self.database = database
        self.message = message
        self.timeout = timeout
        
    @property
    def path(self):
        """Return the path selected in the mongo cluster."""
        path_list = []
        if self.database:
            path_list.append(self.database.name)
        if self.collection:
            path_list.append(self.collection.name)
        if self.post:
            path_list.append(self.post.id)
        return path_list
        
    @path.setter
    def path(self, path_list: list):
        """Set the path of the room."""
        if len(path_list) > 1:
            self.database = cluster[path_list[0]]
        if len(path_list) > 2:
            self.collection = self.database[path_list[1]]
        if len(path_list) > 3:
            self.post = self.collection[path_list[2]]
            
    @path.deleter
    def path(self):
        """Tricky way to set the path to empty."""
        self.database = None
        self.collection = None
        self.post = None
        
    @property
    def embed(self):
        """Update the embed."""
        if self.post:
            return self.embed_post()
        elif self.collection:
            return self.embed_collection()
        elif self.database:
            return self.embed_database()
        else:
            return self.embed_default()
            
    def embed_default(self):
        """Set the embed when nothing is selected."""
        return discord.Embed(
            title="Aucune sélection active",
            description='/'.join(self.path),
            color=self.member.color)
                
    def embed_database(self):
        """Set the embed only when the database is selected."""
        embed = discord.Embed(
            title=self.database.name,
            description='/'.join(self.path),
            color=self.color,
        )
        for k,v in self.database.items():
            embed.add_field(name=k, value=v)
        return embed
            
    def embed_collection(self):
        """Set the embed when the collection and the database
        are selected."""
        embed = discord.Embed(
            title=self.collection.title,
            description='/'.join(self.path),
            color=self.color,
        )
        for k,v in self.collection.items():
            embed.add_field(name=k, value=v)
        return embed
    
    def embed_post(self):
        """Set the embed when the post, the collection and the
        database are selected."""
        embed = discord.Embed(
            title=self.post.id,
            description='/'.join(self.path),
            color=self.color
        )
        for k,v in self.post.items():
            embed.add_field(name=k, value=v)
        return embed
        
    async def show(self, ctx: commands.Context):
        """Send a message one at a time."""
        if self.message: await self.message.delete()
        self.message = await ctx.send(embed=self.embed)
        return await self.add_reactions(ctx):
            
    async def add_reactions(self, ctx):
        """Add the reactions. Bad design."""
        await self.message.add_reaction(emoji.next)
        await self.message.add_reaction(emoji.back)
        await self.message.add_reaction(emoji.trash)
        reactions = [emoji.next, emoji.back, emoji.trash]
        while True:
            try:
                reaction, user = await ctx.bot.wait_for(
                    'reaction_add', timeout=self.timeout, check=lambda r,u:not u.bot)
                await reaction.remove(user)
                if reaction.emoji == emoji.back:
                    self.path = self.path[::-1]
                    return True
                elif reaction.emoji == emoji.trash:
                    return False
            except asyncio.exceptions.TimeoutError:
                return False
            
    def __delitem__(self):
        """Delete the messages when the room is deleted."""
        await self.room.message.delete()


class Mongo(commands.Cog):
    """Catégorie qui permet de naviguer au sein d'un cluster de mongo db."""
    
    def __init__(self, bot: commands.Bot, rooms:dict={}):
        """Initialise la catégorie mongo avec le dictionnaire des salons."""
        self.bot = bot
        self.rooms = rooms

    def __getitem__(self, ctx: commands.Context):
        """Return a room using the context."""
        return self.get_room(ctx.guild.id, ctx.author)
        
    def __delitem__(self, ctx: commands.Context):
        """Delete a room using the context."""
        del self.rooms[ctx.guild.id]
        
    def get_room(self, id: int, member: discord.Member):
        """Return a room using the id and the discord member."""
        if id not in self.rooms:
            self.rooms[id] = MongoRoom(member)
        return self.rooms[id]
        
    @commands.group(aliases=['mg'])
    async def mongo(self, ctx: commands.Context):
       """Groupe de commandes mongo."""
       if not ctx.invoked_subcommand:
        await self.show(ctx)

    @mongo.command(name='afficher', aliases=['a', 'show'])
    async def show(self, ctx: commands.Context):
        """Affiche un salon mongo."""
        room = self[ctx]
        await room.show(ctx)
        
    @mongo.command(name='sélectionner', aliases=['=', 'select'])
    async def select(self, ctx: commands.Context, *path: str):
        """Sélectionne un chemin mongo."""
        room = self[ctx]
        room.path = path
        keeping = await self.show(ctx)
        if not keeping:
            del self[ctx]
        
    @mongo.command(name="chemin", alises=['path'])
    async def path(self, ctx: commands.Context):
        """Affiche le chemin dans le cluster mongo."""
        room = self[ctx]
        print(room.path)
        text_path = '\n'.join(room.path)
        await ctx.send(f"> {text_path}")


def setup(bot):
    """Setup the cog."""
    bot.add_cog(Mongo(bot))